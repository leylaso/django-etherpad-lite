from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import pre_delete
from django.utils.translation import ugettext as _

from py_etherpad import EtherpadLiteClient

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

  def __unicode__(self):
    return self.group.__unicode__()

  def EtherMap(self):
    epclient = EtherpadLiteClient(self.server.apikey, self.server.apiurl)
    result = epclient.createGroupIfNotExistsFor(self.group.id.__str__())

    self.groupID = result['groupID']
    return result

  def save(self, *args, **kwargs):
    self.EtherMap()
    super(PadGroup, self).save(*args, **kwargs)

  def Destroy(self):
    Pad.objects.filter(group=self).delete()  # First find and delete all associated pads
    epclient = EtherpadLiteClient(self.server.apikey, self.server.apiurl)
    result = epclient.deleteGroup(self.groupID)
    return result

def padGroupDel(sender, **kwargs):
  """Make sure groups are purged from etherpad when deleted
  """
  grp = kwargs['instance']
  grp.Destroy()
pre_delete.connect(padGroupDel, sender=PadGroup)

def groupDel(sender, **kwargs):
  """Make sure our groups are destroyed properly when auth groups are deleted
  """
  grp = kwargs['instance']
  padGrp = PadGroup.objects.get(group=grp)
  padGrp.Destroy()
pre_delete.connect(groupDel, sender=Group)


class PadAuthor(models.Model):
  """Schema and methods for etherpad-lite authors
  """
  user = models.ForeignKey(User)
  authorID = models.CharField(max_length=256, blank=True)
  server = models.ForeignKey(PadServer)
  group = models.ManyToManyField(PadGroup, blank=True, null=True)

  class Meta:
    verbose_name = _('author')

  def __unicode__(self):
    return self.user.__unicode__()

  def EtherMap(self):

    epclient = EtherpadLiteClient(self.server.apikey, self.server.apiurl)

    result = epclient.createAuthorIfNotExistsFor(self.user.id.__str__(), name=self.__unicode__())
    self.authorID = result['authorID']

    return result

  def GroupSynch(self, *args, **kwargs):
    for ag in self.user.groups.all():
      try:
        gr = PadGroup.objects.get(group=ag)
      except PadGroup.DoesNotExist:
        gr = False
      if (isinstance(gr, PadGroup)):
        self.group.add(gr)
    super(PadAuthor, self).save(*args, **kwargs)

  def save(self, *args, **kwargs):
    self.EtherMap()
    super(PadAuthor, self).save(*args, **kwargs)


class Pad(models.Model):
  """Schema and methods for etherpad-lite pads
  """
  name = models.CharField(max_length=256)
  server = models.ForeignKey(PadServer)
  group = models.ForeignKey(PadGroup)

  def __unicode__(self):
    return self.name

  @property
  def padid(self):
      return "%s$%s" % (self.group.groupID, self.name)

  def Create(self):
    epclient = EtherpadLiteClient(self.server.apikey, self.server.apiurl)

    result = epclient.createGroupPad(self.group.groupID, self.name)

    return result

  def Destroy(self):
    epclient = EtherpadLiteClient(self.server.apikey, self.server.apiurl)

    result = epclient.deletePad(self.padid)

    return result

  def ReadOnly(self):
    epclient = EtherpadLiteClient(self.server.apikey, self.server.apiurl)

    result = epclient.getReadOnlyID(self.padid)

    return self.server.url + 'ro/' + result['readOnlyID']

  def save(self, *args, **kwargs):
    self.Create()
    super(Pad, self).save(*args, **kwargs)

def padDel(sender, **kwargs):
  """Make sure pads are purged from the etherpad-lite server on deletion
  """
  pad = kwargs['instance']
  pad.Destroy()
pre_delete.connect(padDel, sender=Pad)
