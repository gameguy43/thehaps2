from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import datetime
from email.parser import Parser as emailParser
import StringIO
import rfc822

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

    @classmethod
    def get_message_body_as_one_str(cls, input_message):
        # in: an email.message.Message
        # out: a string, representing the email body
        # TODO
        message_types = [
            "text/html",
            "text/plain"
            ]
        outer_types = [
            'multipart/alternative'
            ]
        ignore_types = [
            ]
        body = ''
        for message in input_message.walk():
            message_type = message.get_content_type()
            if message_type in message_types:
                body += message.get_payload()

        return body

    @classmethod
    def create_and_save_from_email_str(cls, email_str):
        e = cls.create_from_email_str(email_str)
        e.save()
        return e

    @classmethod
    def parse_from_field(cls, from_field):
        # TODO: might want to do some more clever stuff here
        return from_field

    @classmethod
    def create_from_email_str(cls, email_as_str):
        # parse it into an email object
        # shove the unicode email string into a stringio before parsing
        # this is madness. why???
        # because email.parser chokes on unicode. i don't know why.
        # maybe some day we'll be able to do this:
        #parsed_email = emailParser().parsestr(email_as_str)
        # until then:
        parsed_email = emailParser().parse(StringIO.StringIO(email_as_str))
        print parsed_email['From']
        if not parsed_email['From'] and not parsed_email['To'] and not parsed_email['Body']:
            print "error parsing email"
            return HttpResponse("")
        if not parsed_email['From'] or not parsed_email['To']:
            print "email missing crucial field"
            return HttpResponse("")
        e = Email()
        email_obj_field_to_model_field_mappings = {
            'To' : 'to',
            #'From' : 'from_field',
            'Cc' : 'cc',
            'Subject' : 'subject',
            'Return-Path' : 'return_path',
            'X-Original-To' : 'x_original_to',
            'Delivered-To' : 'delivered_to',
            'Received' : 'received',
            'X-Mailer' : 'x_mailer',
            'Message-Id' : 'message_id',
            }
        e.date = datetime.datetime(*rfc822.parsedate_tz(parsed_email['Date'])[:6])
        e.body = cls.get_message_body_as_one_str(parsed_email)
        e.from_field = cls.parse_from_field(parsed_email['From'])
        for email_field, model_field in email_obj_field_to_model_field_mappings.iteritems():
          setattr(e, model_field, parsed_email[email_field])

        # get or create the user who sent this email
        e.user, created = User.objects.get_or_create(email=e.from_email())

        return e

    def from_email(self):
        return self.from_field.split(' ')[0]

    def get_same_emails(self):
        return Email.objects.filter(body=self.body).exclude(id=self.id)

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
        self.calendar_item = c
        self.save()
        return c


def get_same_emails_on_save(sender, instance, created, **kwargs):
    if created:
        same_emails = instance.get_same_emails()
        for same_email in same_emails.all():
            instance.same_emails.add(same_email)
post_save.connect(get_same_emails_on_save, sender=Email)
