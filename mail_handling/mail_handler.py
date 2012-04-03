import sys
import urllib
import datetime
from optparse import OptionParser
import StringIO

def get_from_field_by_force_from_email_str(email_str):
    def get_substr_between_tokens(base_str, token1, token2):
        return base_str.split(token1)[1].split(token2)[0]
    return get_substr_between_tokens(email_str, 'From: ', 'To: ').strip()


SUCCESS_OUTPUT = '1'

remote_url = 'http://calendaritem.com/add/email'
local_url = "http://localhost:8000/add/email"

parser = OptionParser()
# "log" or "only_server_response"
parser.add_option("-o", "--output", action="store", type="string", dest="output", default="log", help="'log' or 'only_server_response'")
# "default" or "local"
parser.add_option("-d", "--destination_url", action="store", type="string", dest="dest_url", default="log", help="where to send the email as post? options are hard-coded in this file. so do one of 'default' or 'local'")
parser.add_option("-i", "--input_file", action="store", type="string", dest="in_file", default="stdin", help="path to sample email file. if stdin (default), just read from stdin (cat the file and pipe to this script)")

(options, args) = parser.parse_args()

if options.dest_url == 'default':
    destination_url = remote_url
elif options.dest_url == 'local':
    destination_url = local_url
else:
    destination_url = remote_url

if options.output == 'log':
    print "======================================"
    print "datetime:"
    print datetime.datetime.now()

fp = sys.stdin
if options.in_file != 'stdin':
    fp = open(options.in_file, 'r')

# get the email as a string
email_str = fp.read()

if options.output == 'log':
    print "email str:"
    print email_str

post_data = {
    'email_str' : email_str,
    }
fp = urllib.urlopen(destination_url,
                    urllib.urlencode(post_data))
output = fp.read()

if options.output == 'log':
    print "server response:"
    print output
    print "-----------------------"
elif options.output == 'only_server_response':
    print output

if output != SUCCESS_OUTPUT:
    from email.parser import Parser as emailParser
    import email.utils
    import smtplib
    from email.mime.text import MIMEText

    # get their email address
    parsed_email = emailParser().parse(StringIO.StringIO(email_str))
    if not parsed_email['From']:
        parsed_email['From'] = get_from_field_by_force_from_email_str(email_str)
    real_name, email_addr = email.utils.parseaddr(parsed_email['From'])
    assert email_addr

    # email them the output
    # assemble the email
    # body:
    to_addr = email_addr
    from_addr = 'robot@calendaritem.com'
    email_strs = ['CalendarItem failed to process your email. Something went horribly wrong. This is super lame and we\'re real sorry about it. Here\'s what the server said:\n\n']
    email_strs.append(output)
    email_strs.append('================================')
    email_strs.append('and here\'s the email you sent us, just to be sure:')
    email_strs.append('================================')
    email_strs.append(email_str)

    # assemble the email object:
    msg = MIMEText('\n'.join(email_strs))
    msg['Subject'] = '[CalendarItem] ERROR! OH NO!'
    msg['From'] = from_addr
    msg['To'] = to_addr

    # send it
    s = smtplib.SMTP('localhost')
    print '============='
    print to_addr
    print '============='
    s.sendmail(from_addr, [to_addr], msg.as_string())
    s.quit()



