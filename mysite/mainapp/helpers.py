from django.contrib.sites.models import Site
from mysite import settings

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
