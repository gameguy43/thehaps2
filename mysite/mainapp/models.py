from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import datetime
from email.parser import Parser as emailParser
import StringIO
import rfc822
import email.utils
import random
import string

from django.template.loader import get_template
from django.template import Context

from mysite.mainapp import helpers

from django.core.mail import send_mail
from django.core.mail import EmailMessage

from django.forms import ModelForm
from django.forms import Textarea

import vobject



CAL_ITEM_TOKEN_LENGTH = 10
FROM_ADDRESS = "robot@calendaritem.com"
EDIT_CAL_ITEM_URL_BASE = helpers.current_site_url() + 'edit/calendaritem/'
class CalendarItem(models.Model):
    # CONSTANTS:

    name = models.CharField(max_length=1000)
    location = models.CharField(max_length=1000)
    info = models.CharField(max_length=90000)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    # used for generating a unique url for /viewing/. not private.
    slug = models.SlugField(max_length=50, unique=True, null=True)
    # private. used for generating a unique url for /editing/
    token = models.SlugField(max_length=50, unique=True, null=True)

    def make_and_set_token(self):
        # TODO: actually, i think i want a separate "Token" module. but this is fine for now.
        self.token =  ''.join(random.choice(string.letters + string.digits) for i in xrange(10))
        self.save()

    def get_url_for_edit(self):
        return EDIT_CAL_ITEM_URL_BASE + self.token

def make_and_set_token_on_save(sender, instance, created, **kwargs):
    if created:
        instance.make_and_set_token()
post_save.connect(make_and_set_token_on_save, sender=CalendarItem)


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    calendar = models.ManyToManyField("CalendarItem")

    def get_ical_feed(self):
        # mega huge ultra thanks to Martin De Wulf:
        # http://www.multitasked.net/2010/jun/16/exporting-schedule-django-application-google-calen/
        cal = vobject.iCalendar()
        cal.add('method').value = 'PUBLISH'  # IE/Outlook needs this
        for c in self.calendar.all():
            vevent = cal.add('vevent')
            vevent.add('dtstart').value = c.start_datetime
            vevent.add('dtend').value = c.end_datetime
            vevent.add('summary').value = c.name
            vevent.add('uid').value = str(c.id)

        return cal.serialize()

    def get_ical_feed_httpresponse(self):
        from django.http import HttpResponse
        response = HttpResponse(self.get_ical_feed(), mimetype='text/calendar')
        response['Filename'] = 'shifts.ics'  # IE needs this
        response['Content-Disposition'] = 'attachment; filename=shifts.ics'
        return response

    def get_name(self):
        if self.user.first_name:
            return self.user.first_name
        else:
            return 'dude'

    def send_email_inviting_to_edit_cal_item(self, cal_item):
        data_for_email_template = {
            'c' : cal_item,
            'userprofile' : self,
            }
        email_str = get_template('edit_new_calendar_item_email.html').render(Context(data_for_email_template))
        email_by_lines = email_str.split('\n')
        email_subject = email_by_lines[0]
        email_body = ''.join(email_by_lines[1:])
        msg = EmailMessage(email_subject, email_body, FROM_ADDRESS, [self.user.email])
        msg.content_subtype = "html"
        msg.send()

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if not instance.userprofile:
            UserProfile.objects.create(user=instance)
post_save.connect(create_user_profile, sender=User)
        

class Email(models.Model):
    # http://en.wikipedia.org/wiki/Email#Header_fields
    # PARSED FROM EMAIL:
    subject = models.CharField(max_length=1000)
    body = models.TextField()
    # note: odd name below because from is a special word
    from_field = models.CharField(max_length=1000)
    to = models.CharField(max_length=1000)
    cc = models.CharField(max_length=1000, null=True, default="")
    date = models.DateTimeField()
    return_path = models.CharField(max_length=1000, null=True, default="")
    x_original_to = models.CharField(max_length=1000, null=True, default="")
    delivered_to =  models.CharField(max_length=1000, null=True, default="")
    received =  models.CharField(max_length=1000, null=True, default="")
    x_mailer =  models.CharField(max_length=1000, null=True, default="")
    message_id =  models.CharField(max_length=1000, null=True, default="")
    
    # OTHER FIELDS:
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
    def create_from_email_str(cls, email_as_str):
        # parse it into an email object
        # shove the unicode email string into a stringio before parsing
        # this is madness. why???
        # because email.parser chokes on unicode. i don't know why.
        # maybe some day we'll be able to do this:
        #parsed_email = emailParser().parsestr(email_as_str)
        # until then:
        parsed_email = emailParser().parse(StringIO.StringIO(email_as_str))
        if not parsed_email['From'] and not parsed_email['To'] and not parsed_email['Body']:
            #import ipdb; ipdb.set_trace()
            print "error parsing email"
            # for now, just explode:
            assert False
        if not parsed_email['From'] or not parsed_email['To']:
            print "email missing crucial field"
            # for now, just explode:
            assert False
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
        e.from_field = parsed_email['From'] #cls.parse_from_field(parsed_email['From'])
        for email_field, model_field in email_obj_field_to_model_field_mappings.iteritems():
          setattr(e, model_field, parsed_email[email_field])

        # get or create the user who sent this email
        assert True # TODO: DEBUG
        e.user, created = User.objects.get_or_create(email=e.from_email())
        e.save() #TODO: might not be necessary. not sure.
        assert e.user

        return e

    def from_email(self):
        '''return only the email address part of the from field'''
        real_name, email_addr = email.utils.parseaddr(self.from_field)
        return email_addr

    def to_email(self):
        '''return only the email address part of the from field'''
        real_name, email_addr = email.utils.parseaddr(self.to)
        return email_addr


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
        assert c
        return c


def get_same_emails_on_save(sender, instance, created, **kwargs):
    if created:
        same_emails = instance.get_same_emails()
        for same_email in same_emails.all():
            instance.same_emails.add(same_email)
post_save.connect(get_same_emails_on_save, sender=Email)




class CalendarItemForm(ModelForm):
    class Meta:
        model = CalendarItem
        exclude = ('slug', 'token')
        widgets = {
            'info': Textarea(attrs={'cols': 20, 'rows': 10}),
            }
