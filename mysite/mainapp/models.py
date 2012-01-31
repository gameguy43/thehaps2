from django.db import models

# Create your models here.

class Email(models.Model):
    # http://en.wikipedia.org/wiki/Email#Header_fields
    subject = models.CharField(max_length=1000)
    body = models.TextField()
    # note: odd name below because from is a special word
    from_field = models.CharField(max_length=100)
    to = models.CharField(max_length=1000)
    cc = models.CharField(max_length=1000, null=True, default="")
    date = models.DateTimeField()
    return_path = models.CharField(max_length=1000, null=True, default="")
    x_original_to = models.CharField(max_length=1000, null=True, default="")
    delivered_to =  models.CharField(max_length=1000, null=True, default="")
    received =  models.CharField(max_length=1000, null=True, default="")
    x_mailer =  models.CharField(max_length=1000, null=True, default="")
    message_id =  models.CharField(max_length=1000, null=True, default="")

    def from_email(self):
        return self.from_field.split(' ')[0]
        
'''
Return-Path
X-Original-To
Delivered-To
Received
X-Mailer
Message-Id
Date
From
Subject
To
'''



class CalendarItem(models.Model):
    name =  models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    info = models.CharField(max_length=100)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    slug = models.SlugField(max_length=50, unique=True, null=True)
