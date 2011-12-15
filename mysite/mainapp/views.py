from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core import serializers
from django.utils import simplejson
from django.contrib.sites.models import Site
import pytz
import hashlib

from mysite.mainapp.models import CalendarItem

import datetime



def to_gcal(request, slug):
    #get the calendar item
    c = CalendarItem.objects.get(slug=slug)
    #get the gcal url
    gcal_url = google_url_from_calendaritem_dict(c.__dict__)
    return HttpResponseRedirect(gcal_url)

def main(request):
    data = {}
    return render_to_response('index.html', data)

def ajax_add_event(request):
    post_data = simplejson.loads(request.raw_post_data)
    post_data = map(lambda d: (d['name'], d['value']), post_data)
    post_data = dict(post_data)

    # parsing the input dates and times
    tz = post_data.get('timezone', None) 
    tz = pytz.timezone(tz)
    start_date = post_data.get('start_date', None) 
    start_time = post_data.get('start_time', None) 
    end_date = post_data.get('end_date', None) 
    end_time = post_data.get('end_time', None) 
    # error out if we didn't get them
    if not (start_date and start_time and end_date and end_time):
        print "didn't get the stuff that we wanted"
        return HttpResponse(simplejson.dumps({ 'status': 400, 'message': 'couldn\'t find the time parameters'}), status=400)
    start_date_m, start_date_d, start_date_y = map(int, start_date.split('/'))
    end_date_m, end_date_d, end_date_y = map(int, end_date.split('/'))
    start_time_h, start_time_m = map(int, start_time.split(':'))
    end_time_h, end_time_m = map(int, end_time.split(':'))
    start_datetime = datetime.datetime(start_date_y, start_date_m, start_date_d, start_time_h, start_time_m, tzinfo=tz)
    end_datetime = datetime.datetime(end_date_y, end_date_m, end_date_d, end_time_h, end_time_m, tzinfo=tz)

    # convert to utc and then naiveify
    # note: we need to naive-ify or else heroku will aggressively try to convert to another timezone at insertion time
    start_datetime, end_datetime = map(lambda dt: dt.astimezone(pytz.utc).replace(tzinfo=None), [start_datetime, end_datetime])

    # make the calendaritem
    c = CalendarItem()
    c.name = post_data.get('title', '')
    c.location = post_data.get('location', '')
    c.info = post_data.get('info', '')
    c.start_datetime = start_datetime
    c.end_datetime  = end_datetime
    c.save()
    #TODO: handle collisions
        # what error will it throw? catch that
    c.slug = generate_hash(c.id)
    c.save()

    #gcal_url = google_url_from_calendaritem_dict(c.__dict__)
    our_url = current_site_url() + '/' + c.slug
    return_dict = {'our_url': our_url}
    return HttpResponse(simplejson.dumps(return_dict), mimetype='application/x-javascript')

def generate_hash(salt):
    salt = str(salt)
    h = hashlib.md5()
    h.update(salt)
    return h.hexdigest()[:5]

def query_str_from_dict(values):
    partial = values.items()
    partial = map(lambda x: map(str, x), partial)
    partial = map('='.join, partial)
    partial = '&'.join(partial)
    return partial
    
def google_url_from_calendaritem_dict(calitem_dict):
    '''docs: http://www.google.com/googlecalendar/event_publisher_guide_detail.html'''
    dt_format = '%Y%m%dT%H%M00Z'
    google_dates = '/'.join(map(lambda dt: dt.strftime(dt_format), [calitem_dict['start_datetime'], calitem_dict['end_datetime']]))
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

def current_site_url():
    """Returns fully qualified URL (no trailing slash) for the current site."""
    current_site = Site.objects.get_current()
    #protocol = getattr(settings, 'MY_SITE_PROTOCOL', 'http')
    protocol = 'http'
    #port = getattr(settings, 'MY_SITE_PORT', '')
    url = '%s://%s' % (protocol, current_site.domain)
    return url
