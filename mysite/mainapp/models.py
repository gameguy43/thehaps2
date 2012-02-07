from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

class CalendarItem(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    info = models.CharField(max_length=100)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    slug = models.SlugField(max_length=50, unique=True, null=True)

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    calendar = models.ManyToManyField("CalendarItem")
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            UserProfile.objects.create(user=instance)
    post_save.connect(create_user_profile, sender=User)

class Email(models.Model):
    # http://en.wikipedia.org/wiki/Email#Header_fields
    #PARSED FROM EMAIL:
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
    
    #OTHER FIELDS:
    user = models.ForeignKey(User, related_name="%(app_label)s_%(class)s_related", null=True)
    calendar_item = models.ForeignKey(CalendarItem, related_name="%(app_label)s_%(class)s_related", null=True)
    same_emails = models.ManyToManyField("self")

    def from_email(self):
        return self.from_field.split(' ')[0]

    def get_same_emails(self):
        #TODO: make this smarter
        return Email.objects.filter(body=self.body)

    def get_same_emails_on_save(sender, instance, created, **kwargs):
        if created:
            same_emails = instance.get_same_emails()
            instance.same_emails.add(same_emails)
    post_save.connect(get_same_emails_on_save, sender='Email')

    def create_auto_parse_calendar_item(self):
        '''Parse the text of an email and come up with a best guess cal item
            Save that cal item and return it'''
        c = CalendarItem()
        c.name = self.subject
        c.location = "A cool place"
        c.info = self.body
        c.start_datetime = datetime.datetime.now()
        c.end_datetime = datetime.datetime.now()
        c.save()
        return c
