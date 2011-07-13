from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core import serializers
from django.utils import simplejson
from mysite.urlgen import urlGen

from mysite.mainapp.models import CalendarItem

import datetime




def main(request):
    data = {}
    return render_to_response('index.html', data)

def ajax_add_event(request):
    '''
    name =  models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    info = models.CharField(max_length=100)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    '''
    # parsing the input dates and times
    start_date = request.POST.get('', None) 
    start_time = request.POST.get('', None) 
    end_date = request.POST.get('', None) 
    end_time = request.POST.get('', None) 
    if not (start_date and start_time and end_date and end_time):
        EXPLODEEEEE
        return False
    start_date_m, start_date_d, start_date_y = start_date.split('/')
    end_date_m, end_date_d, end_date_y = end_date.split('/')
    start_time_h, start_time_m = start_time_time.split(':')
    end_time_h, end_m = end_time.split(':')
    start_datetime = datetime.datetime(start_date_y, start_date_m, start_date_d, start_time_h, start_time_m)
    end_datetime = datetime.datetime(end_date_y, end_date_m, end_date_d, end_time_h, end_time_m)

    c = CalendarItem()
    c.name = request.POST.get('title', '')
    c.location = request.POST.get('location', '')
    c.info = request.POST.get('info', '')
    c.start_datetime = start_datetime
    c.end_datetime  = end_datetime
    c.save()

    response = google_url_from_calendaritem_dict(d.__dict__())
    return HttpResponse(response, mimetype='text/html')

def query_str_from_dict(values):
    partial = values.items()
    partial = map(lambda x: map(str, x), partial)
    partial = map('='.join, partial)
    partial = '&'.join(partial)
    return partial
    
def google_url_from_calendaritem_dict(calitem_dict):
    google_dates = '1' #TODO
    google_query_str = {
        'action' : 'TEMPLATE',
        'text' : calitem_dict.get('name', ''),
        'dates' : google_dates,
        'details' : calitem_dict.get('info', ''),
        'location' : calitem_dict.get('location', ''),
        'trp' : 'false',
        }

    '''
    action=TEMPLATE
    text=My%20sweet%20event
    dates=20110710T070000Z/20060101T080000Z
    details=hiiiii
    location=here
    trp=false
    sprop=http%3A%2F%2Fmadebyparker.com
    sprop=name:Parker%20Phinney

    http://www.google.com/calendar/event?action=TEMPLATE&text=My%20sweet%20event&dates=20110710T070000Z/20060101T080000Z&details=hiiiii&location=here&trp=false&sprop=http%3A%2F%2Fmadebyparker.com&sprop=name:Parker%20Phinney
    '''
    google_url_base = 'http://www.google.com/calendar/event?'
    google_query_str = query_str_from_dict(google_query_str)
    google_url = ''.join([google_url_base, google_query_str])
    return google_url
