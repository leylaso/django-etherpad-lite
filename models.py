from django.db import models
from django.contrib.auth.models import User, Group
from django_etherpad_lite import simplecurl

# Create your models here.

class PadServer(models.Model):
  title = models.CharField(max_length=256)
  url = models.URLField(max_length=256, verify_exists=False)
  apikey = models.CharField(max_length=256) 
  notes = models.TextField('Description', blank=True)
  def __unicode__(self):
    return self.url

class PadGroup(models.Model):
  group = models.ForeignKey(Group, verbose_name='Group')
  groupID = models.CharField(max_length=256, blank=True)
  server = models.ForeignKey(PadServer, verbose_name='Serveur')
  def __unicode__(self):
    return self.group.__unicode__()
  def EtherMap(self):
    req = self.server.url + 'api/1/createGroupIfNotExistsFor?apikey=' + self.server.apikey + '&groupMapper=' + self.group.id.__str__()
    result = simplecurl.json(req)
    self.groupID = result['data']['groupID']
    self.save()
    return result

class PadAuthor(models.Model):
  user = models.ForeignKey(User, verbose_name='User')
  authorID = models.CharField(max_length=256, blank=True)
  server = models.ForeignKey(PadServer, verbose_name='Serveur')
  group = models.ManyToManyField(PadGroup, blank=True, null=True, verbose_name='Group')
  def __unicode__(self):
    return self.user.__unicode__()
  def EtherMap(self):
    req = self.server.url + 'api/1/createAuthorIfNotExistsFor?apikey=' + self.server.apikey + '&name=' + self.__unicode__() + '&authorMapper=' + self.user.id.__str__()
    result = simplecurl.json(req)
    self.authorID = result['data']['authorID']
    self.save()
    for g in self.group.all():
      g.EtherMap()
    return result

class Pad(models.Model):
  name = models.CharField(max_length=256)
  server = models.ForeignKey(PadServer, verbose_name='Serveur')
  group = models.ForeignKey(PadGroup, verbose_name='Group')
  def __unicode__(self):
    return self.name
  def Create(self):
    req = self.server.url + 'api/1/createGroupPad?apikey=' + self.server.apikey + '&groupID=' + self.group.groupID + '&padName=' + self.name
    result = simplecurl.json(req)
    return result

class PadSession(models.Model):
  group = models.ForeignKey(PadGroup, verbose_name='Group')
  author = models.ForeignKey(PadAuthor, verbose_name='Auteur')
  sessionID = models.CharField(max_length=256, blank=True)
  def __unicode__(self):
    return self.author + '@' + self.group
