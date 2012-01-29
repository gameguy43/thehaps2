import sys
from email.parser import Parser

#process_from = 'stdin'
process_from = 'file'
in_file = '/tmp/sample_msg.email'

def main():
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

main()
