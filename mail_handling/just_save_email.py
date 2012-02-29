import sys
from email.parser import Parser

process_from = 'stdin'
#process_from = 'file'
in_file = "sample_msg.email" # not used for process_from = stdin
out_file = '/tmp/outfile.txt'

def just_save_email():
    '''utility for generating a test email file'''
    # grab a file pointer for our email
    if process_from == 'stdin':
        fp = sys.stdin
    elif process_from == 'file':
        fp = open(in_file, 'r')
        pass
    else:
        print "something terrible has happened"
        return
    # get the email as a string
    email_str = fp.read()

    f = open(out_file, 'w')
    f.write(email_str)

just_save_email()
