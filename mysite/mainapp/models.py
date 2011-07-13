from django.db import models

# Create your models here.

class CalendarItem(models.Model):
    name =  models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    info = models.CharField(max_length=100)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
