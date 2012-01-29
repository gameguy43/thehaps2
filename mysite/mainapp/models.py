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

class CalendarItem(models.Model):
    name =  models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    info = models.CharField(max_length=100)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    slug = models.SlugField(max_length=50, unique=True, null=True)
