# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'Email.cc'
        db.alter_column('mainapp_email', 'cc', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True))


    def backwards(self, orm):
        
        # Changing field 'Email.cc'
        db.alter_column('mainapp_email', 'cc', self.gf('django.db.models.fields.CharField')(default=None, max_length=1000))


    models = {
        'mainapp.calendaritem': {
            'Meta': {'object_name': 'CalendarItem'},
            'end_datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'info': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'unique': 'True', 'null': 'True', 'db_index': 'True'}),
            'start_datetime': ('django.db.models.fields.DateTimeField', [], {})
        },
        'mainapp.email': {
            'Meta': {'object_name': 'Email'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'cc': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1000', 'null': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'from_field': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'to': ('django.db.models.fields.CharField', [], {'max_length': '1000'})
        }
    }

    complete_apps = ['mainapp']
