"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test import Client
from mysite.mainapp.models import Email

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.failUnlessEqual(1 + 1, 2)

class EmailTest(TestCase):
    def do_test_email_adding_to_db(self, email_str, email_data):

        the_subject = email_data['subject']
        the_body = email_data['body']
        the_sender_address = email_data['sender_address']

        # send the email to the post handler
        c = Client()
        data = {'email_str': email_str}
        c.post('/add/email', data)

        # test that we have an email with that subject
        e = Email.objects.get(subject=the_subject)
        self.assertEqual(e.body, the_body)

        # test that the sender address is correct
        self.assertEqual(e.user.email, the_sender_address)

        # test that there is now an event with that title in the user's calendar
        self.assertTrue(len(e.user.userprofile.calendar.filter(name=the_subject)) > 0)

        # NOTE: side-effects below this line. we're doing another insertion
        # send that same email again.
        # want to make sure the system notices they're the same email
        c.post('/add/email', data)

        # test that the two emails in our database know they're the same
        e1, e2 = Email.objects.all()
        self.assertEqual(e1.same_emails.all()[:1][0], e2)
        self.assertEqual(e2.same_emails.all()[:1][0], e1)

    def test_email_adding_to_db_simple(self):
        # get the test email
        test_email_filename = 'mainapp/test_data/sample_msg.email'
        test_email_str = open(test_email_filename, 'r').read()
        # hard code the fields to test against
        # in other words, these are the "expected values"
        test_email_data =  {
            'subject': 'yo dog',
            'body': 'asdfsadf',
            'sender_address': "pyrak@parktop.com",
            }
        self.do_test_email_adding_to_db(test_email_str, test_email_data)

    def test_email_adding_to_db_fusion_dance_show(self):
        # get the test email
        test_email_filename = 'mainapp/test_data/forwarded_email_fusion_show.email'
        test_email_str = open(test_email_filename, 'r').read()
        # hard code the fields to test against
        # in other words, these are the "expected values"
        test_email_data =  {
            'subject': 'yo dog',
            'body': 'asdfsadf',
            'sender_address': "pyrak@parktop.com",
            }
        self.do_test_email_adding_to_db(test_email_str, test_email_data)

    def test_email_adding_to_db_causes_email_to_user(self)
        #TODO:
        # forward an email invite
        # make sure that we've generated a secret query string var for them to edit the event info
        # make sure that we've sent the user an email
        # make sure the email we sent includes the event title

        self.assertTrue(False)
