from django.shortcuts import render_to_response
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core import serializers
from django.utils import simplejson
from django.db import IntegrityError

from mysite.mainapp.models import CalendarItem
from mysite.mainapp.models import UserProfile
from mysite.mainapp.models import CalendarItemForm
from mysite.mainapp.models import Email

from mysite.mainapp import utils


from django.contrib.auth.models import User

import os
import pytz
import datetime

from django.template import RequestContext

from mysite.mainapp import helpers

from mysite import settings


def to_gcal(request, slug):
    #get the calendar item
    c = CalendarItem.objects.get(slug=slug)
    #get the gcal url
    gcal_url = utils.google_url_from_calendaritem_dict(c.__dict__)
    return HttpResponseRedirect(gcal_url)

def main(request):

#    import gflags
#    import httplib2
#
#    from apiclient.discovery import build
#    from oauth2client.file import Storage
#    from oauth2client.client import OAuth2WebServerFlow
#    from oauth2client.client import OAuth2Credentials
#    from oauth2client.tools import run
#
#    FLAGS = gflags.FLAGS
#
#    # Set up a Flow object to be used if we need to authenticate. This
#    # sample uses OAuth 2.0, and we set up the OAuth2WebServerFlow with
#    # the information it needs to authenticate. Note that it is called
#    # the Web Server Flow, but it can also handle the flow for native
#    # applications
#    # The client_id and client_secret are copied from the API Access tab on
#    # the Google APIs Console
#    FLOW = OAuth2WebServerFlow(
#        client_id = settings.GOOGLE_CLIENT_ID,
#        client_secret = settings.GOOGLE_CLIENT_SECRET,
#        scope = 'https://www.googleapis.com/auth/calendar',
#        user_agent = 'calendaritem.com')
#
#    # To disable the local server feature, uncomment the following line:
#    FLAGS.auth_local_webserver = False
#
#    # If the Credentials don't exist or are invalid, run through the native client
#    # flow. The Storage object will ensure that if successful the good
#    # Credentials will get written back to a file.
#    storage = Storage('calendar.dat')
#    credentials = storage.get()
#    if credentials is None or credentials.invalid == True:
#        credentials = run(FLOW, storage)
#
#    '''
#    credentials = OAuth2Credentials(
#        access_token = '',
#        refresh_token = '',
#        token_expiry = '',
#        token_uri = '',
#
#        client_id = settings.GOOGLE_CLIENT_ID,
#        client_secret = settings.GOOGLE_CLIENT_SECRET,
#        #scope = 'https://www.googleapis.com/auth/calendar',
#        user_agent = 'calendaritem.com')
#    '''
#
#
#    # Create an httplib2.Http object to handle our HTTP requests and authorize it
#    # with our good Credentials.
#    http = httplib2.Http()
#    http = credentials.authorize(http)
#
#    # Build a service object for interacting with the API. Visit
#    # the Google APIs Console
#    # to get a developerKey for your own application.
#    service = build(serviceName='calendar', version='v3', http=http,
#        developerKey=settings.GOOGLE_DEVELOPER_KEY)
#
#

    #return render(request, 'index.html', context_instance=RequestContext(request))
    return render(request, 'index.html')

def json_str_to_dict(json_str):
    def strip_newlines_from_str(string):
        return '\\n'.join(string.splitlines())
    def return_newlines(string):
        return string.replace('\\n', '\n')
    #escape newlines because they break the JSON parser
    json_str = strip_newlines_from_str(json_str)
    json_data = simplejson.loads(json_str)
    json_data = dict([(d['name'], return_newlines(d['value']))
                 for d in json_data])
    return json_data

def add_email_do(request):
    # grab the email from post
    email_as_str = request.POST['email_str']
    e = Email.create_and_save_from_email_str(email_as_str)
    c = None
    # case: we already have this email
    if e.same_emails.exists():
        # grab the associated event from the database
        # (just assume that the first same email speaks for them all)
        c = e.same_emails.all()[:1][0].calendar_item
    # case: this email is new to the system
    # we didn't make this an else because we also want to create in the case
    # where we had a previous email but no calendar item for it
    if not c:
        # come up with our best guess parse of the event info
        # also, create a new event for it and put it in the database
        c = e.create_auto_parse_calendar_item()
    
    # add the event to their event list
    assert c
    e.user.userprofile.calendar.add(c)

    # send confirmation email with the event info (inviting them to modify)
    e.user.userprofile.send_email_inviting_to_edit_cal_item(c)

    return HttpResponse("1")

def show_current_user_calendar(request):
    return show_user_calendar(request, user_id=request.user.pk)


def show_user_calendar(request, user_id):
    # get the calendar items
    calendar_items = User.objects.get(pk=user_id).userprofile.calendar.all()
    # show them
    data = {
        'calendar_items' : calendar_items,
        }
    return render(request, 'show_user_calendar.html', data)
    

def edit_calendaritem(request, token):
    success = False
    c = CalendarItem.objects.get(token=token)
    # TODO: handle case where we can't get that calendar item
    # if they submitted the form, handle it:
    if request.POST:
        form = CalendarItemForm(request.POST, instance=c)
        if form.is_valid():
            form.save()
            # TODO: if this was an ajax request, just return a success JSON message
            success = True

    else:
        form = CalendarItemForm(instance=c)

    data = {
        'success' : success,
        'form' : form,
        'c' : c,
        }
    return render(request, 'edit_cal_item.html', data)

def calendar_feed(request, user_id):
    userprofile = User.objects.get(pk=user_id).userprofile
    return userprofile.get_ical_feed_httpresponse()

def ajax_add_event(request):
    #decoding the inputted JSON blob
    json_data = request.POST['data_as_json']
    post_data = json_str_to_dict(json_data)

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

    tries_left = 3
    while tries_left >= 0:
        tries_left-=1
        c.slug = utils.generate_hash(c.id)
        try:
            c.save()
            break
        except IntegrityError:
            print "slug collision. re-rolling..."
            continue
        except:
            print "trouble putting the calendar item in the database"
            return HttpResponse(simplejson.dumps({ 'status': 400, 'message': 'couldn\'t put calendar item in the database'}), status=400)
    #if we tried X times and didn't get a slug that we could use...
    if tries_left <0:
        print "rolled X times and couldn't get a good slug"
        return HttpResponse(simplejson.dumps({ 'status': 400, 'message': 'couldn\'t get a good slug after X rolls'}), status=400)

    #gcal_url = google_url_from_calendaritem_dict(c.__dict__)
    our_url = helpers.current_site_url() + c.slug
    return_dict = {'our_url': our_url}
    return HttpResponse(simplejson.dumps(return_dict), mimetype='application/x-javascript')

