import sys
from email.parser import Parser
import urllib
import datetime


#JUST_SAVE_EMAIL = True
JUST_SAVE_EMAIL = False

process_from = 'stdin'
#process_from = 'file'
in_file = './sample_msg.email'

destination_url = 'http://calendaritem.com/add/email'

def lightweight_handler():
    '''send the email to the site as plaintext in POST data'''
    print "======================================"
    print "datetime::"
    print datetime.datetime.now()
    # grab a file pointer for our email
    if process_from == 'stdin':
        fp = sys.stdin
    elif process_from == 'file':
        fp = open(in_file, 'r')
    else:
        print "something terrible has happened"
        return
    # get the email as a string
    email_str = fp.read()
    print "email str:"
    print email_str
    post_data = {
        'email_str' : email_str,
        }
    fp = urllib.urlopen(destination_url,
                        urllib.urlencode(post_data))
    output = fp.read()
    print "server response:"
    print output
    print "-----------------------"
    return output

if JUST_SAVE_EMAIL:
    import just_save_email
    just_save_email.just_save_email()
else:
    output = lightweight_handler()
    print output
