# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'PadServer'
        db.create_table('etherpadlite_padserver', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=256)),
            ('apikey', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('etherpadlite', ['PadServer'])

        # Adding model 'PadGroup'
        db.create_table('etherpadlite_padgroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.Group'])),
            ('groupID', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('server', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['etherpadlite.PadServer'])),
        ))
        db.send_create_signal('etherpadlite', ['PadGroup'])

        # Adding model 'PadAuthor'
        db.create_table('etherpadlite_padauthor', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('authorID', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('server', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['etherpadlite.PadServer'])),
        ))
        db.send_create_signal('etherpadlite', ['PadAuthor'])

        # Adding M2M table for field group on 'PadAuthor'
        db.create_table('etherpadlite_padauthor_group', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('padauthor', models.ForeignKey(orm['etherpadlite.padauthor'], null=False)),
            ('padgroup', models.ForeignKey(orm['etherpadlite.padgroup'], null=False))
        ))
        db.create_unique('etherpadlite_padauthor_group', ['padauthor_id', 'padgroup_id'])

        # Adding model 'Pad'
        db.create_table('etherpadlite_pad', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('server', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['etherpadlite.PadServer'])),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['etherpadlite.PadGroup'])),
        ))
        db.send_create_signal('etherpadlite', ['Pad'])


    def backwards(self, orm):
        # Deleting model 'PadServer'
        db.delete_table('etherpadlite_padserver')

        # Deleting model 'PadGroup'
        db.delete_table('etherpadlite_padgroup')

        # Deleting model 'PadAuthor'
        db.delete_table('etherpadlite_padauthor')

        # Removing M2M table for field group on 'PadAuthor'
        db.delete_table('etherpadlite_padauthor_group')

        # Deleting model 'Pad'
        db.delete_table('etherpadlite_pad')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'etherpadlite.pad': {
            'Meta': {'object_name': 'Pad'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['etherpadlite.PadGroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['etherpadlite.PadServer']"})
        },
        'etherpadlite.padauthor': {
            'Meta': {'object_name': 'PadAuthor'},
            'authorID': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'authors'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['etherpadlite.PadGroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['etherpadlite.PadServer']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'etherpadlite.padgroup': {
            'Meta': {'object_name': 'PadGroup'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.Group']"}),
            'groupID': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['etherpadlite.PadServer']"})
        },
        'etherpadlite.padserver': {
            'Meta': {'object_name': 'PadServer'},
            'apikey': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '256'})
        }
    }

    complete_apps = ['etherpadlite']