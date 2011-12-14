# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'CalendarItem.slug'
        db.add_column('mainapp_calendaritem', 'slug', self.gf('django.db.models.fields.SlugField')(max_length=50, unique=True, null=True, db_index=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'CalendarItem.slug'
        db.delete_column('mainapp_calendaritem', 'slug')


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
        }
    }

    complete_apps = ['mainapp']
