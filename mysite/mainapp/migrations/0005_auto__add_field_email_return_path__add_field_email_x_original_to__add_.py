# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Email.return_path'
        db.add_column('mainapp_email', 'return_path', self.gf('django.db.models.fields.CharField')(default='', max_length=1000, null=True), keep_default=False)

        # Adding field 'Email.x_original_to'
        db.add_column('mainapp_email', 'x_original_to', self.gf('django.db.models.fields.CharField')(default='', max_length=1000, null=True), keep_default=False)

        # Adding field 'Email.delivered_to'
        db.add_column('mainapp_email', 'delivered_to', self.gf('django.db.models.fields.CharField')(default='', max_length=1000, null=True), keep_default=False)

        # Adding field 'Email.received'
        db.add_column('mainapp_email', 'received', self.gf('django.db.models.fields.CharField')(default='', max_length=1000, null=True), keep_default=False)

        # Adding field 'Email.x_mailer'
        db.add_column('mainapp_email', 'x_mailer', self.gf('django.db.models.fields.CharField')(default='', max_length=1000, null=True), keep_default=False)

        # Adding field 'Email.message_id'
        db.add_column('mainapp_email', 'message_id', self.gf('django.db.models.fields.CharField')(default='', max_length=1000, null=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Email.return_path'
        db.delete_column('mainapp_email', 'return_path')

        # Deleting field 'Email.x_original_to'
        db.delete_column('mainapp_email', 'x_original_to')

        # Deleting field 'Email.delivered_to'
        db.delete_column('mainapp_email', 'delivered_to')

        # Deleting field 'Email.received'
        db.delete_column('mainapp_email', 'received')

        # Deleting field 'Email.x_mailer'
        db.delete_column('mainapp_email', 'x_mailer')

        # Deleting field 'Email.message_id'
        db.delete_column('mainapp_email', 'message_id')


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
            'delivered_to': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1000', 'null': 'True'}),
            'from_field': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1000', 'null': 'True'}),
            'received': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1000', 'null': 'True'}),
            'return_path': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1000', 'null': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'to': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'x_mailer': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1000', 'null': 'True'}),
            'x_original_to': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1000', 'null': 'True'})
        }
    }

    complete_apps = ['mainapp']
