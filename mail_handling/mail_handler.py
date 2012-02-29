import sys
import urllib
import datetime
from optparse import OptionParser

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
