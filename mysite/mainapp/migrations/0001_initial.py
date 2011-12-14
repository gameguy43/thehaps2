# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'CalendarItem'
        db.create_table('mainapp_calendaritem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('info', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('start_datetime', self.gf('django.db.models.fields.DateTimeField')()),
            ('end_datetime', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('mainapp', ['CalendarItem'])


    def backwards(self, orm):
        
        # Deleting model 'CalendarItem'
        db.delete_table('mainapp_calendaritem')


    models = {
        'mainapp.calendaritem': {
            'Meta': {'object_name': 'CalendarItem'},
            'end_datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'info': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'start_datetime': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['mainapp']
