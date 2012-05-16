from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import datetime
import time
from email.parser import Parser as emailParser
import StringIO
import rfc822
import email.utils
from django.utils import http
import random
import string

from django.template.loader import get_template
from django.template import Context


from django.core.mail import send_mail
from django.core.mail import EmailMessage

from django.core.urlresolvers import reverse

from django.forms import ModelForm
from django.forms import Textarea

import vobject

from django.utils.html import strip_tags

from mysite.mainapp import utils

import django.forms as forms





CAL_ITEM_TOKEN_LENGTH = 10
FROM_ADDRESS = '"CalendarItem Robot" <add@calendaritem.com>'
EDIT_CAL_ITEM_URL_BASE = utils.current_site_url() + 'edit/calendaritem/'

class EmailAddress(models.Model):
    user = models.ForeignKey(User, related_name="%(app_label)s_%(class)s_related")
    email_address = models.CharField(max_length=1000)

    @classmethod
    def get_or_create_user_with_address(cls, email_address):
        email_address_objects = cls.objects.filter(email_address=email_address)
        if email_address_objects:
            return email_address_objects[0].user
        else:
            users = User.objects.filter(email=email_address)
        if users:
            return users[0]
        else:
            return User.objects.create(email=email_address)

    @classmethod
    def backpopulate_for_existing_users(cls):
        for user in User.objects.all():
            cls.objects.create(user=user, email_address=user.email_address)

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

    def make_and_set_slug(self):
        slug = utils.generate_hash(self.id)
        utils.unique_slugify(self, slug)
        self.save()

    def get_url_for_edit(self):
        return EDIT_CAL_ITEM_URL_BASE + self.token

    def get_url_for_add_to_gcal(self):
        return utils.google_url_from_calendaritem_dict(self.__dict__)

    def get_url_for_cal_item(self):
        assert self.slug
        return utils.current_site_url() + str(self.slug)

def make_and_set_token_on_save(sender, instance, created, **kwargs):
    if created:
        instance.make_and_set_token()
post_save.connect(make_and_set_token_on_save, sender=CalendarItem)

def make_and_set_slug_on_save(sender, instance, created, **kwargs):
    if created:
        instance.make_and_set_slug()
post_save.connect(make_and_set_slug_on_save, sender=CalendarItem)


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    calendar = models.ManyToManyField("CalendarItem")
    timezone = models.CharField(max_length=100)


    def claim_email_address(self, email_address):
        # make an emailaddress
        EmailAddress.objects.get_or_create(email_address=email_address, user=self.user)
        # if there's already a user with this email address:
        existing_users = User.objects.filter(email=email_address)
        if existing_users:
            existing_user = existing_users[0]
            for c in existing_user.userprofile.calendar.all():
                self.calendar.add(c)
                self.save()
            existing_user.delete()

    def get_url_for_ical_feed(self):
        # NOTE: we slice out the first char of the reverse() result because it's just a slash
        return utils.current_site_url() + reverse('calendar_feed', kwargs={'user_id': self.user.id})[1:]

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
        REFRESH_RATE_SECONDS = 60
        from django.http import HttpResponse
        response = HttpResponse(self.get_ical_feed(), mimetype='text/calendar')
        response['Filename'] = 'calendar.ics'  # IE needs this
        response['Content-Disposition'] = 'attachment; filename=calendar.ics'
        response['Expires'] = http.http_date(time.time() + REFRESH_RATE_SECONDS)
        return response

    def get_name(self):
        if self.user.first_name:
            return self.user.first_name
        else:
            return 'dude'

    def send_email_inviting_to_edit_cal_item(self, cal_item, email=None):
        data_for_email_template = {
            'c' : cal_item,
            'userprofile' : self,
            }
        email_body = get_template('edit_new_calendar_item_email.html').render(Context(data_for_email_template))

        #make the subject
        if email:
            email_subject = 'Re: ' + email.subject
        else:
            email_subject = '[CalendarItem] NEW: ' + c.name

        msg = EmailMessage(email_subject, email_body, FROM_ADDRESS, [self.user.email])
        msg.content_subtype = "html"
        msg.send()

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if not UserProfile.objects.filter(user=instance):
            UserProfile.objects.create(user=instance)
post_save.connect(create_user_profile, sender=User)

def create_user_email_address(sender, instance, created, **kwargs):
    if created:
        EmailAddress.objects.create(user=instance, email_address=instance.email)
post_save.connect(create_user_email_address, sender=User)
        

class Email(models.Model):
    # http://en.wikipedia.org/wiki/Email#Header_fields
    # PARSED FROM EMAIL:
    plaintext = models.CharField(max_length=90000)
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
        e.plaintext = email_as_str
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
        e.user = EmailAddress.get_or_create_user_with_address(e.from_email())
        #e.user, created = User.objects.get_or_create(email=e.from_email())
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


    def walk_email_until_we_get_to_the_bottom(self):
        return self.body
        #message_types = [
        #    "text/html",
        #    "text/plain"
        #    ]
        ##TODO: we need to actually think of this as a tree, i think.
        #semantic_body = emailParser().parse(StringIO.StringIO(self.body))
        #bottom_message = '[[DEFAULT]]'
        #for message_piece in semantic_body.walk():
        #    if type(message_piece) in (str, unicode):
        #        bottom_message = message_piece
        #    elif message_type in message_piece.get_content_type():
        #        bottom_message = message_piece
        #return bottom_message

    def get_interesting_part_of_body(self):
        bottom_message_str = self.walk_email_until_we_get_to_the_bottom()

        # the action starts after the second occurrance of 'Forwarded message'
        GMAIL_FORWARDED_MSG_MARKER = '---------- Forwarded message ----------'
        if GMAIL_FORWARDED_MSG_MARKER in bottom_message_str:
            split = bottom_message_str.split(GMAIL_FORWARDED_MSG_MARKER)
            try:
                bottom_message_str = split[2]
            except:
                bottom_message_str = split[1]

        # the action starts after the /first/ "To:" line
        TO_MARKER = 'To: '
        if TO_MARKER in bottom_message_str:
            bottom_message_str = bottom_message_str.split(TO_MARKER)[1]

        # remove html tags from the email
        bottom_message_str = strip_tags(bottom_message_str)
        bottom_message_str = utils.unescape(bottom_message_str)
        return bottom_message_str
    
    def get_interesting_part_of_subject(self):
        subject = self.subject
        FWD_PREFIX = 'Fwd: '
        if FWD_PREFIX in subject:
            subject = subject.split(FWD_PREFIX)[1]
        return subject

    def create_auto_parse_calendar_item(self):
        '''Parse the text of an email and come up with a best guess cal item
            Save that cal item and return it'''
        c = CalendarItem()
        c.name = self.get_interesting_part_of_subject()
        c.location = "Somewhere"
        c.info = self.get_interesting_part_of_body()
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



class AugmentedSplitDateTimeWidget(forms.SplitDateTimeWidget):
    """
    A Widget that splits datetime input into two <input type="text"> boxes.
    """

    def __init__(self, class_prefix='', attrs={}, date_format=None, time_format=None):

        date_input_attrs, time_input_attrs = attrs.copy(), attrs.copy()
        date_input_attrs['class'] = class_prefix + '_date'
        time_input_attrs['class'] = class_prefix + '_time'
        assert date_input_attrs.copy()
        assert time_input_attrs.copy()
        widgets = (forms.DateInput(attrs=date_input_attrs, format='%m/%d/%Y'),
                   forms.TimeInput(attrs=time_input_attrs, format='%H:%M'))
        super(forms.SplitDateTimeWidget, self).__init__(widgets, attrs)


class CalendarItemForm(ModelForm):
    class Meta:
        model = CalendarItem
        exclude = ('slug', 'token')
        widgets = {
            'info': Textarea(attrs={'cols': 20, 'rows': 20}),
            'start_datetime': AugmentedSplitDateTimeWidget(class_prefix='start'),
            'end_datetime': AugmentedSplitDateTimeWidget(class_prefix='end'),
            }
