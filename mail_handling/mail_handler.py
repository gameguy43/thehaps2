import sys
from email.parser import Parser
import urllib


#JUST_SAVE_EMAIL = True
JUST_SAVE_EMAIL = False

process_from = 'stdin'
#process_from = 'file'
in_file = '/tmp/sample_msg.email'

destination_url = 'http://calendaritem.com/add/email'

def lightweight_handler():
    '''send the email to the site as plaintext in POST data'''
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
    post_data = {
        'email_str' : email_str,
        }
    fp = urllib.urlopen(destination_url,
                        urllib.urlencode(post_data))
    return fp.read()

if JUST_SAVE_EMAIL:
    import just_save_email
    just_save_email.just_save_email()
else:
    output = lightweight_handler()
    print output
