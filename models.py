from django.db import models
from django.contrib.auth.models import User, Group

# Create your models here.

class PadServer(models.Model):
  title = models.CharField(max_length=256)
  url = models.URLField(max_length=256)
  apikey = models.CharField(max_length=256) 
  notes = models.TextField('Description', blank=True)
  def __unicode__(self):
    return self.url

class PadGroup(models.Model):
  group = models.ForeignKey(Group, verbose_name='Group')
  groupID = models.CharField(max_length=256)
  server = models.ForeignKey(PadServer, verbose_name='Serveur')
  def __unicode__(self):
    return self.groupID

class PadAuthor(models.Model):
  user = models.ForeignKey(User, verbose_name='User')
  authorID = models.CharField(max_length=256)
  server = models.ForeignKey(PadServer, verbose_name='Serveur')
  group = models.ManyToManyField(PadGroup, blank=True, null=True, verbose_name='Group')
  def __unicode__(self):
    return self.authorID

class Pad(models.Model):
  name = models.CharField(max_length=256)
  server = models.ForeignKey(PadServer, verbose_name='Serveur')
  group = models.ForeignKey(PadGroup, verbose_name='Group')
  def __unicode__(self):
    return self.name

class PadSession(models.Model):
  group = models.ForeignKey(PadGroup, verbose_name='Group')
  author = models.ForeignKey(PadAuthor, verbose_name='Auteur')
  sessionID = models.CharField(max_length=256, blank=True)
  def __unicode__(self):
    return self.sessionID
