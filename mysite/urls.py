from django.conf.urls.defaults import *
from django.conf import settings


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # for admin docs:
    # also add 'django.contrib.admindocs' to INSTALLED_APPS
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # admin enabled:
    (r'^admin/', include(admin.site.urls)),

    (r'^$', 'mysite.mainapp.views.main'),
    (r'^ajax_add_event$', 'mysite.mainapp.views.ajax_add_event'),

    (r'^add/email$', 'mysite.mainapp.views.add_email_do'),
    (r'^edit/calendaritem/(?P<token>\w+)$', 'mysite.mainapp.views.edit_calendaritem'),



    # to allow static files to be served by django (band-aid for now)
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.STATIC_DOC_ROOT, 'show_indexes': True}),
    (r'^images/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.STATIC_DOC_ROOT + 'images/', 'show_indexes': True}),

    (r'^(?P<user_id>\d+)/feed.ics$', 'mysite.mainapp.views.calendar_feed'),

    # gotta go last because everything matches this pattern
    (r'^(?P<slug>\w+)$', 'mysite.mainapp.views.to_gcal'),
)
