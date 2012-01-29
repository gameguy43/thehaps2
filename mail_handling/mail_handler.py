import sys
from email.parser import Parser
import urllib

#process_from = 'stdin'
process_from = 'file'
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
    #print fp.read() #DEBUG


def main():
    '''this does a bit more processing of the data. but we should move the processing code to the main server. the goal of this file is just to convert an email into a post request in real time'''
    # grab a file pointer for our email
    if process_from == 'stdin':
        fp = sys.stdin
    elif process_from == 'file':
        fp = open(in_file, 'r')
    else:
        print "something terrible has happened"
        return
    parsed = Parser().parse(fp)
    import ipdb ; ipdb.set_trace()
    f.write(str(parsed))

def just_save_email():
    '''utility for generating a test email file'''
    f = open('/tmp/outfile.txt', 'w')
    f.write(in_text)

lightweight_handler()
