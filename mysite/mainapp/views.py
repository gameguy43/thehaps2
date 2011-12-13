from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core import serializers
from django.utils import simplejson

from mysite.mainapp.models import CalendarItem

import datetime




def main(request):
    data = {}
    return render_to_response('index.html', data)

def ajax_add_event(request):
    post_data = simplejson.loads(request.raw_post_data)
    post_data = map(lambda d: (d['name'], d['value']), post_data)
    post_data = dict(post_data)

    # parsing the input dates and times
    utc_offset = post_data.get('utc_offset', 0) 
    start_date = post_data.get('start_date', None) 
    start_time = post_data.get('start_time', None) 
    end_date = post_data.get('end_date', None) 
    end_time = post_data.get('end_time', None) 
    # error out if we didn't get them
    if not (start_date and start_time and end_date and end_time):
        print "didn't get the stuff that we wanted"
        return HttpResponse(simplejson.dumps({ 'status': 400, 'message': 'couldn\'t find the time parameters'}), status=400)


        return False
    start_date_m, start_date_d, start_date_y = map(int, start_date.split('/'))
    end_date_m, end_date_d, end_date_y = map(int, end_date.split('/'))
    start_time_h, start_time_m = map(int, start_time.split(':'))
    end_time_h, end_time_m = map(int, end_time.split(':'))
    start_datetime = datetime.datetime(start_date_y, start_date_m, start_date_d, start_time_h, start_time_m)
    start_datetime = start_datetime + datetime.timedelta(minutes=utc_offset)
    end_datetime = datetime.datetime(end_date_y, end_date_m, end_date_d, end_time_h, end_time_m)
    end_datetime = end_datetime + datetime.timedelta(minutes=utc_offset)

    c = CalendarItem()
    c.name = post_data.get('title', '')
    c.location = post_data.get('location', '')
    c.info = post_data.get('info', '')
    c.start_datetime = start_datetime
    c.end_datetime  = end_datetime
    c.save()

    gcal_url = google_url_from_calendaritem_dict(c.__dict__)
    return_dict = {'google_url': gcal_url}
    return HttpResponse(simplejson.dumps(return_dict), mimetype='application/x-javascript')

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
