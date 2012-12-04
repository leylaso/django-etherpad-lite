from django.db import models
from django.db.models.signals import pre_delete
from django.contrib.auth.models import User, Group
from django.utils.translation import ugettext_lazy as _

from py_etherpad import EtherpadLiteClient

import string
import random

class PadServer(models.Model):
    """Schema and methods for etherpad-lite servers
    """
    title = models.CharField(max_length=256)
    url = models.URLField(
        max_length=256,
        verify_exists=False,
        verbose_name=_('URL')
    )
    apikey = models.CharField(max_length=256, verbose_name=_('API key'))
    notes = models.TextField(_('description'), blank=True)

    class Meta:
        verbose_name = _('server')

    def __unicode__(self):
        return self.url

    @property
    def apiurl(self):
        if self.url[-1:] == '/':
            return "%sapi" % self.url
        else:
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

    @property
    def epclient(self):
        return EtherpadLiteClient(self.server.apikey, self.server.apiurl)

    def _get_random_id(self, size=6,
        chars=string.ascii_uppercase + string.digits + string.ascii_lowercase):
        """ To make the ID unique, we generate a randomstring
        """
        return ''.join(random.choice(chars) for x in range(size))    

    def EtherMap(self):
        result = self.epclient.createGroupIfNotExistsFor(
            self.group.__unicode__() + self._get_random_id() +
            self.group.id.__str__()
        )
        self.groupID = result['groupID']
        return result

    def save(self, *args, **kwargs):
        if not self.id:
            self.EtherMap()
        super(PadGroup, self).save(*args, **kwargs)

    def Destroy(self):
        # First find and delete all associated pads
        Pad.objects.filter(group=self).delete()
        return self.epclient.deleteGroup(self.groupID)


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
    # Make shure auth groups without a pad group can be deleted, too.
    try:
        padGrp = PadGroup.objects.get(group=grp)
        padGrp.Destroy()
    except Exception:
        pass
pre_delete.connect(groupDel, sender=Group)


class PadAuthor(models.Model):
    """Schema and methods for etherpad-lite authors
    """
    user = models.ForeignKey(User)
    authorID = models.CharField(max_length=256, blank=True)
    server = models.ForeignKey(PadServer)
    group = models.ManyToManyField(
        PadGroup,
        blank=True,
        null=True,
        related_name='authors'
    )

    class Meta:
        verbose_name = _('author')

    def __unicode__(self):
        return self.user.__unicode__()

    def EtherMap(self):
        epclient = EtherpadLiteClient(self.server.apikey, self.server.apiurl)
        result = epclient.createAuthorIfNotExistsFor(
            self.user.id.__str__(),
            name=self.__unicode__()
        )
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

    @property
    def epclient(self):
        return EtherpadLiteClient(self.server.apikey, self.server.apiurl)

    def Create(self):
        return self.epclient.createGroupPad(self.group.groupID, self.name)

    def Destroy(self):
        return self.epclient.deletePad(self.padid)

    def isPublic(self):
        result = self.epclient.getPublicStatus(self.padid)
        return result['publicStatus']

    def ReadOnly(self):
        return self.epclient.getReadOnlyID(self.padid)

    def save(self, *args, **kwargs):
        self.Create()
        super(Pad, self).save(*args, **kwargs)


def padDel(sender, **kwargs):
    """Make sure pads are purged from the etherpad-lite server on deletion
    """
    pad = kwargs['instance']
    pad.Destroy()
pre_delete.connect(padDel, sender=Pad)
