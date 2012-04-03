import sys
import urllib
import datetime
from optparse import OptionParser
import StringIO


SUCCESS_OUTPUT = '1'

remote_url = 'http://calendaritem.com/add/email'
local_url = "http://localhost:8000/add/email"

parser = OptionParser()
# "log" or "only_server_response"
parser.add_option("-o", "--output", action="store", type="string", dest="output", default="log", help="'log' or 'only_server_response'")
# "default" or "local"
parser.add_option("-d", "--destination_url", action="store", type="string", dest="dest_url", default="log", help="where to send the email as post? options are hard-coded in this file. so do one of 'default' or 'local'")
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

# grab a file pointer for our email
fp = sys.stdin
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
    real_name, email_addr = email.utils.parseaddr(parsed_email['From'])

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
    s.sendmail(from_addr, [to_addr], msg.as_string())
    s.quit()
