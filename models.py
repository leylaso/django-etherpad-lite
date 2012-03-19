from django.db import models
from django.contrib.auth.models import User, Group
from django_etherpad_lite import simplecurl
from django.db.models.signals import pre_delete
from django.utils.translation import ugettext as tr


class PadServer(models.Model):
  """Schema and methods for etherpad-lite servers
  """
  title = models.CharField(max_length=256)
  url = models.URLField(max_length=256, verify_exists=False, verbose_name=tr('URL'))
  apikey = models.CharField(max_length=256, verbose_name=tr('API key')) 
  notes = models.TextField(tr('description'), blank=True)

  class Meta:
    verbose_name = tr('server')

  def __unicode__(self):
    return self.url


class PadGroup(models.Model):
  """Schema and methods for etherpad-lite groups
  """
  group = models.ForeignKey(Group)
  groupID = models.CharField(max_length=256, blank=True)
  server = models.ForeignKey(PadServer)

  class Meta:
    verbose_name = tr('group')

  def __unicode__(self):
    return self.group.__unicode__()

  def EtherMap(self):
    req = self.server.url + 'api/1/createGroupIfNotExistsFor?apikey=' + self.server.apikey + '&groupMapper=' + self.group.id.__str__()
    result = simplecurl.json(req)
    self.groupID = result['data']['groupID']
    return result

  def save(self, *args, **kwargs):
    self.EtherMap()
    super(PadGroup, self).save(*args, **kwargs)

  def Destroy(self):
    Pad.objects.filter(group=self).delete()  # First find and delete all associated pads
    req = self.server.url + 'api/1/deleteGroup?apikey=' + self.server.apikey + '&groupID=' + self.groupID
    result = simplecurl.json(req)
    return result

def padGroupDel(sender, **kwargs):
  """Make sure groups are purged from etherpad when deleted
  """
  grp = kwargs['instance']
  grp.Destroy()
pre_delete.connect(padGroupDel, sender=PadGroup)


class PadAuthor(models.Model):
  """Schema and methods for etherpad-lite authors
  """
  user = models.ForeignKey(User)
  authorID = models.CharField(max_length=256, blank=True)
  server = models.ForeignKey(PadServer)
  group = models.ManyToManyField(PadGroup, blank=True, null=True)

  class Meta:
    verbose_name = tr('author')

  def __unicode__(self):
    return self.user.__unicode__()

  def EtherMap(self):
    req = self.server.url + 'api/1/createAuthorIfNotExistsFor?apikey=' + self.server.apikey + '&name=' + self.__unicode__() + '&authorMapper=' + self.user.id.__str__()
    result = simplecurl.json(req)
    self.authorID = result['data']['authorID']
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
    self.GroupSynch() # Unfortunately, this will only work when save is called from code


class Pad(models.Model):
  """Schema and methods for etherpad-lite pads
  """
  name = models.CharField(max_length=256)
  server = models.ForeignKey(PadServer)
  group = models.ForeignKey(PadGroup)

  def __unicode__(self):
    return self.name

  def Create(self):
    req = self.server.url + 'api/1/createGroupPad?apikey=' + self.server.apikey + '&groupID=' + self.group.groupID + '&padName=' + self.name
    result = simplecurl.json(req)
    return result

  def Destroy(self):
    req = self.server.url + 'api/1/deletePad?apikey=' + self.server.apikey + '&padID=' + self.group.groupID + '$' + self.name
    result = simplecurl.json(req)
    return result

  def ReadOnly(self):
    req = self.server.url + 'api/1/getReadOnlyID?apikey=' + self.server.apikey + '&padID=' + self.group.groupID + '$' + self.name
    result = simplecurl.json(req)
    return self.server.url + 'ro/' + result['data']['readOnlyID']

  def save(self, *args, **kwargs):
    self.Create()
    super(Pad, self).save(*args, **kwargs)

def padDel(sender, **kwargs):
  """Make sure pads are purged from the etherpad-lite server on deletion
  """
  pad = kwargs['instance']
  pad.Destroy()
pre_delete.connect(padDel, sender=Pad)
