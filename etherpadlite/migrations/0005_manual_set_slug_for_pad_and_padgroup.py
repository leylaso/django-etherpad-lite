# -*- coding: utf-8 -*-
from south.v2 import SchemaMigration
from django.template.defaultfilters import slugify


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding slug to field 'PadGroup.slug'
        for i in orm['etherpadlite.PadGroup'].all():
            i.slug = slugify(i.group.name)
            i.save()

        # Adding slug to field 'Pad.slug'
        for i in orm['etherpadlite.Pad'].all():
            i.slug = slugify(i.name)
            i.save()

    def backwards(self, orm):
        """
        """
