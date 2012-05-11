import re
from htmlentitydefs import name2codepoint
# for some reason, python 2.5.2 doesn't have this one (apostrophe)
name2codepoint['#39'] = 39

def unescape(s):
    "unescape HTML code refs; c.f. http://wiki.python.org/moin/EscapingHtml"
    return re.sub('&(%s);' % '|'.join(name2codepoint),
                  lambda m: unichr(name2codepoint[m.group(1)]), s)


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



