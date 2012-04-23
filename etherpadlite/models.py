from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import pre_delete, pre_save
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from py_etherpad import EtherpadLiteClient
from django.db.models.loading import get_model   

import urllib
import types
import hashlib

def get_group_model(): 
  model_name = getattr(settings, 'ETHERPAD_GROUP_MODEL', 'django.contrib.auth.Group')
  group_app, group_model = model_name.rsplit('.', 1)
  GroupModel = get_model(group_app, group_model)
  return GroupModel


class PadServer(models.Model):
  """Schema and methods for etherpad-lite servers
  """
  title = models.CharField(max_length=256)
  url = models.URLField(max_length=256, verify_exists=False, verbose_name=_('URL'))
  apikey = models.CharField(max_length=256, verbose_name=_('API key')) 
  notes = models.TextField(_('description'), blank=True)

  class Meta:
    verbose_name = _('server')

  def __unicode__(self):
    return self.url

  @property
  def apiurl(self):
    return "%s/api" % self.url


class PadGroup(models.Model):
  """Schema and methods for etherpad-lite groups
  """
  group = models.ForeignKey(Group)
  groupID = models.CharField(max_length=256, blank=True)
  server = models.ForeignKey(PadServer)

  class Meta:
    verbose_name = _('group')

  def __init__(self, *args, **kwargs):
    super(PadGroup, self).__init__(*args, **kwargs)
    self.epclient = EtherpadLiteClient(self.server.apikey, self.server.apiurl)

  @property
  def _group(self):
    GroupModel = get_group_model()
    reverse_field_name = getattr(settings, 'ETHERPAD_GROUP_FIELD_NAME', 'profile_group')

    if getattr(self, reverse_field_name, None) is not None:
        return getattr(self, reverse_field_name)

    field_name = getattr(settings, 'ETHERPAD_GROUP_PAD_FIELD_NAME', 'pad_group')

    if field_name not in [f.name for f in GroupModel._meta.fields]:
      raise Exception('Field %s not found on model %s' % (field_name, model_name))

    return GroupModel.objects.get(**{field_name: self})      

  def __unicode__(self):
    return self._group.__unicode__()

  def map_to_etherpad(self):
    result = self.epclient.createGroupIfNotExistsFor(self._group.id.__str__())
    self.groupID = result['groupID']

  def Destroy(self):
    Pad.objects.filter(group=self).delete()  # First find and delete all associated pads
    try:
        result = self.epclient.deleteGroup(self.groupID)
    except ValueError, e:
        # Already gone? Good.
        pass


class PadAuthor(models.Model):
  """Schema and methods for etherpad-lite authors
  """
  user = models.ForeignKey(User)
  authorID = models.CharField(max_length=256, blank=True)
  server = models.ForeignKey(PadServer)
  group = models.ManyToManyField(PadGroup, blank=True, null=True, related_name='authors')

  class Meta:
    verbose_name = _('author')

  def __init__(self, *args, **kwargs):
    super(PadAuthor, self).__init__(*args, **kwargs)
    self.epclient = EtherpadLiteClient(self.server.apikey, self.server.apiurl)

  def __unicode__(self):
    return self.user.__unicode__()

  def map_to_etherpad(self):

    default_author_name_mapper = lambda user: user.__unicode__()
    author_name_mapper = getattr(settings, 'ETHERPAD_AUTHOR_NAME_MAPPER', default_author_name_mapper)

    if not isinstance(author_name_mapper, types.FunctionType):
      author_name_mapper = default_author_name_mapper

    result = self.epclient.createAuthorIfNotExistsFor(self.user.id.__str__(), name=author_name_mapper(self.user))
    self.authorID = result['authorID']


  def GroupSynch(self, *args, **kwargs):

    members_field_name = getattr(settings, 'ETHERPAD_GROUP_USERS_FIELD_NAME', 'user_set')
    pad_field_name = getattr(settings, 'ETHERPAD_GROUP_PAD_FIELD_NAME', 'pad_group')

    GroupModel = get_group_model()

    groups = GroupModel.objects.filter(**{"%s__in" % members_field_name: [self.user.id]})

    for ag in groups:
      try:
        gr = getattr(GroupModel.objects.get(**{pad_field_name: self}), pad_field_name)
      except GroupModel.DoesNotExist:
        gr = False
      if (isinstance(gr, PadGroup)):
        self.group.add(gr)


class Pad(models.Model):
  """Schema and methods for etherpad-lite pads
  """
  name = models.CharField(max_length=256)
  server = models.ForeignKey(PadServer)
  group = models.ForeignKey(PadGroup)

  def __unicode__(self):
    return self.name

  def __init__(self, *args, **kwargs):
    super(Pad, self).__init__(*args, **kwargs)
    self.epclient = EtherpadLiteClient(self.server.apikey, self.server.apiurl)

  @property
  def md5hash(self):
      return hashlib.md5(self.name.encode('utf-8')).hexdigest()

  @property
  def padid(self):
      return "%s$%s" % (self.group.groupID, self.md5hash)

  @property
  def ro_id(self):
      result = self.epclient.getReadOnlyID(self.padid)
      return result['readOnlyID']

  @property
  def link(self):
      return "%sp/%s" % (self.server.url, urllib.quote_plus(self.padid))

  @property
  def ro_link(self):
      return "%sro/%s" % (self.server.url, self.ro_id)
      
  def Create(self):
    result = self.epclient.createGroupPad(self.group.groupID, self.md5hash)

  def Destroy(self):
    try:
        result = self.epclient.deletePad(self.padid)
    except ValueError, e:
        # Already gone? Good.
        pass

  def isPublic(self):
    result = self.epclient.getPublicStatus(self.padid)
    return result['publicStatus']

  def ReadOnly(self):
      return self.ro_link


def padCreate(sender, instance, **kwargs):
  instance.Create()
pre_save.connect(padCreate, sender=Pad)

def padDel(sender, instance, **kwargs):
  instance.Destroy()
pre_delete.connect(padDel, sender=Pad)
pre_delete.connect(padDel, sender=PadGroup)

def padObjectPreSave(sender, instance, **kwargs):
  instance.map_to_etherpad()
pre_save.connect(padObjectPreSave, sender=PadGroup)
pre_save.connect(padObjectPreSave, sender=PadAuthor)


def groupDel(sender, instance, **kwargs):

  # We are trying to make this work generically for (almost) any
  # group-like model Therefore, this signal listens to every
  # pre_delete and filters on the actual model

  GroupModel = get_group_model()

  if GroupModel != sender:
    return 
 
  field_name = getattr(settings, 'ETHERPAD_GROUP_PAD_FIELD_NAME', 'pad_group')

  if field_name not in [f.name for f in GroupModel._meta.fields]:
    return 

  padGrp = getattr(GroupModel.objects.get(pk=instance.id), field_name, None)

  if padGrp is None:
    return

  padGrp.Destroy()

pre_delete.connect(groupDel)
