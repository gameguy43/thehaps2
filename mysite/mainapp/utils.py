import os
import re
import hashlib
from htmlentitydefs import name2codepoint
# for some reason, python 2.5.2 doesn't have this one (apostrophe)
name2codepoint['#39'] = 39

from django.contrib.sites.models import Site
from django.template.defaultfilters import slugify
from mysite import settings

import datetime
import dateutil.parser
import pytz

GOOGLE_DT_FORMAT = '%Y%m%dT%H%M00Z'


def text_to_cal_item_dict(text):
    return text_to_cal_item_dict_via_google(text)

def text_to_cal_item_dict_via_google(text):
    # thanks to https://github.com/insanum/gcalcli
    # used you as a reference

    from gdata.calendar.service import *

    gcal = CalendarService()
    gcal.ssl = True

    SOURCE = 'calendaritem.com'
    SERVICE = 'cl'
    USERNAME = settings.GOOGLE_QUICK_ADD_USER
    PASSWORD = settings.GOOGLE_QUICK_ADD_PASSWORD

     # authenticate and login to google calendar
    try:
        gcal.ClientLogin(
                         username=USERNAME,
                         password=PASSWORD,
                         service=SERVICE,
                         source=SOURCE)
    except Exception, e:
        print ("Error: " + str(e) + "!\n")

    target_calendar = '/calendar/feeds/default/private/full'

    quickEvent = gdata.calendar.CalendarEventEntry()
    quickEvent.content = atom.Content(text=text)
    quickEvent.quick_add = gdata.calendar.QuickAdd(value='true')

    event = gcal.InsertEvent(quickEvent, target_calendar)

    event_info_dict = {}

    event_info_dict['name'] = event.title.text
    event_info_dict['info'] = ''

    event_info_dict['start_datetime'] = event.when[0].start_time
    event_info_dict['start_datetime'] = dateutil.parser.parse(event_info_dict['start_datetime'])

    event_info_dict['end_datetime'] = event.when[0].end_time
    event_info_dict['end_datetime'] = dateutil.parser.parse(event_info_dict['end_datetime'])

    event_info_dict['location'] = event.where[0].value_string

    return event_info_dict

def naiveify_datetime(dt):
    return dt.astimezone(pytz.utc).replace(tzinfo=None)


def current_site_url():
    """Returns fully qualified URL (WITH trailing slash) for the current site."""

    # setttings.py approach:
    return settings.BASE_URL_WITH_TRAILING_SLASH

    # Django sites framework approach:
    #current_site = Site.objects.get_current()
    ##protocol = getattr(settings, 'MY_SITE_PROTOCOL', 'http')
    #protocol = 'http'
    ##port = getattr(settings, 'MY_SITE_PORT', '')
    #url = '%s://%s/' % (protocol, current_site.domain)
    #return url

def unescape(s):
    "unescape HTML code refs; c.f. http://wiki.python.org/moin/EscapingHtml"
    return re.sub('&(%s);' % '|'.join(name2codepoint),
                  lambda m: unichr(name2codepoint[m.group(1)]), s)


def google_url_from_calendaritem_dict(calitem_dict):
    '''docs: http://www.google.com/googlecalendar/event_publisher_guide_detail.html'''
    google_dates = '/'.join(map(lambda dt: dt.strftime(GOOGLE_DT_FORMAT), [calitem_dict['start_datetime'], calitem_dict['end_datetime']]))
    google_query_str = {
        'action' : 'TEMPLATE',
        'text' : calitem_dict.get('name', ''),
        'dates' : google_dates,
        'details' : calitem_dict.get('info', ''),
        'location' : calitem_dict.get('location', ''),
        }

    google_url_base = 'http://www.google.com/calendar/event?'
    google_query_str = query_str_from_dict(google_query_str)
    google_url = ''.join([google_url_base, google_query_str])
    return google_url

def generate_hash(x):
    x = str(x)
    # insert some randomness so that we can "re-roll" our slugs
    salt = os.urandom(3)
    x+= salt
    h = hashlib.md5()
    h.update(x)
    return h.hexdigest()[:5]

def query_str_from_dict(values):
    partial = values.items()
    partial = map(lambda x: map(str, x), partial)
    partial = map('='.join, partial)
    partial = '&'.join(partial)
    return partial
    
def url_with_query_str_vars(url, query_str_vars_as_dict):
    # TODO: edit this to notice if there are already query str vars and act accordingly
    # for now, this will do horrible things unless the url currently has no question mark
    return url + '?' + urllib.urlencode(query_str_vars_as_dict)


# thanks, http://djangosnippets.org/snippets/690/

def unique_slugify(instance, value, slug_field_name='slug', queryset=None,
                   slug_separator='-'):
    """
    Calculates and stores a unique slug of ``value`` for an instance.

    ``slug_field_name`` should be a string matching the name of the field to
    store the slug in (and the field to check against for uniqueness).

    ``queryset`` usually doesn't need to be explicitly provided - it'll default
    to using the ``.all()`` queryset from the model's default manager.
    """
    slug_field = instance._meta.get_field(slug_field_name)

    slug = getattr(instance, slug_field.attname)
    slug_len = slug_field.max_length

    # Sort out the initial slug, limiting its length if necessary.
    slug = slugify(value)
    if slug_len:
        slug = slug[:slug_len]
    slug = _slug_strip(slug, slug_separator)
    original_slug = slug

    # Create the queryset if one wasn't explicitly provided and exclude the
    # current instance from the queryset.
    if queryset is None:
        queryset = instance.__class__._default_manager.all()
    if instance.pk:
        queryset = queryset.exclude(pk=instance.pk)

    # Find a unique slug. If one matches, at '-2' to the end and try again
    # (then '-3', etc).
    next = 2
    while not slug or queryset.filter(**{slug_field_name: slug}):
        slug = original_slug
        end = '%s%s' % (slug_separator, next)
        if slug_len and len(slug) + len(end) > slug_len:
            slug = slug[:slug_len-len(end)]
            slug = _slug_strip(slug, slug_separator)
        slug = '%s%s' % (slug, end)
        next += 1

    setattr(instance, slug_field.attname, slug)


def _slug_strip(value, separator='-'):
    """
    Cleans up a slug by removing slug separator characters that occur at the
    beginning or end of a slug.

    If an alternate separator is used, it will also replace any instances of
    the default '-' separator with the new separator.
    """
    separator = separator or ''
    if separator == '-' or not separator:
        re_sep = '-'
    else:
        re_sep = '(?:-|%s)' % re.escape(separator)
    # Remove multiple instances and if an alternate separator is provided,
    # replace the default '-' separator.
    if separator != re_sep:
        value = re.sub('%s+' % re_sep, separator, value)
    # Remove separator from the beginning and end of the slug.
    if separator:
        if separator != '-':
            re_sep = re.escape(separator)
        value = re.sub(r'^%s+|%s+$' % (re_sep, re_sep), '', value)
    return value
