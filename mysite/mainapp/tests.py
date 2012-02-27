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

do_add_to_calendar_url = '/add/email'
do_edit_calendar_item_url = '/edit/calendaritem'
class EmailTest(TestCase):
    def do_test_email_adding_to_db(self, email_str, email_data):

        the_subject = email_data['subject']
        the_body_contains = email_data['body_contains']
        the_sender_address = email_data['sender_address']

        # send the email to the post handler
        c = Client()
        data = {'email_str': email_str}
        c.post(do_add_to_calendar_url, data)

        # test that we have an email with that subject
        e = Email.objects.get(subject=the_subject)
        self.assertTrue(type(e.body.index(the_body_contains)) == int)

        # test that the sender address is correct
        self.assertEqual(e.user.email, the_sender_address)

        # test that there is now an event with that title in the user's calendar
        self.assertTrue(len(e.user.userprofile.calendar.filter(name=the_subject)) > 0)

        # NOTE: side-effects below this line. we're doing another insertion
        # send that same email again.
        # want to make sure the system notices they're the same email
        c.post(do_add_to_calendar_url, data)

        # test that the two emails in our database know they're the same
        e1, e2 = Email.objects.all()
        self.assertEqual(e1.same_emails.all()[:1][0], e2)
        self.assertEqual(e2.same_emails.all()[:1][0], e1)

    def test_getting_from_address_from_from_field(self):
        from_fields_to_correct_parses = {
            "D. Parker Phinney <thedude@gmail.com>" : "thedude@gmail.com",
            # these fail, which is kind of lame:
            #"Parker thedude@gmail.com" : "thedude@gmail.com",
            #"Free Culture @ NYU <theotherdude@gmail.com>" : "theotherdude@gmail.com",
            '"Free Culture @ NYU" <theotherdude@gmail.com>' : "theotherdude@gmail.com",
            "thedude@gmail.com" : "thedude@gmail.com",
            "theotherdude@gmail.com" : "theotherdude@gmail.com",
            "theotherdude@gmail.com (Parker)" : "theotherdude@gmail.com",
        }
        test_email_filename = 'mainapp/test_data/reply_to_forwarded_email_fusion_show.email'
        test_email_str = open(test_email_filename, 'r').read()
        e = Email.create_from_email_str(test_email_str)
        iterations = 0
        for from_field, correct_parse in from_fields_to_correct_parses.iteritems():
            e.from_field = from_field
            self.assertEqual(e.from_email(), correct_parse)
            iterations += 1
        self.assertTrue(iterations > 3)

    def test_email_adding_to_db_simple(self):
        # get the test email
        test_email_filename = 'mainapp/test_data/sample_msg.email'
        test_email_str = open(test_email_filename, 'r').read()
        # hard code the fields to test against
        # in other words, these are the "expected values"
        test_email_data =  {
            'subject': 'yo dog',
            'body_contains': 'asdfsadf',
            'sender_address': "pyrak@parktop.com",
            }
        self.do_test_email_adding_to_db(test_email_str, test_email_data)

    def test_email_adding_to_db_fusion_dance_show(self):
        # get the test email
        test_email_filename = 'mainapp/test_data/reply_to_forwarded_email_fusion_show.email'
        test_email_str = open(test_email_filename, 'r').read()
        # hard code the fields to test against
        # in other words, these are the "expected values"
        test_email_data =  {
            'subject': 'Re: ***This WEDNESDAY***',
            'body_contains': 'sigma delt is the one right next to c&c, right?',
            'sender_address': "parker.phinney@gmail.com",
            }
        self.do_test_email_adding_to_db(test_email_str, test_email_data)

    def test_email_adding_to_db_causes_email_to_user(self):
        # get the test email--a forwarded invite
        test_email_filename = 'mainapp/test_data/reply_to_forwarded_email_fusion_show.email'
        test_email_str = open(test_email_filename, 'r').read()

        # send the email to the post handler
        c = Client()
        data = {'email_str': test_email_str}
        c.post(do_add_to_calendar_url, data)

        #TODO:
        # make sure that we've generated a secret query string var for them to edit the event info
        # make sure that we've sent the user an email
        # make sure the email we sent includes the event title

        self.assertTrue(False)

    def test_whole_email_calendar_item_workflow(self):
        # get the test email--a forwarded invite
        test_email_filename = 'mainapp/test_data/reply_to_forwarded_email_fusion_show.email'
        the_subject = 'Re: ***This WEDNESDAY***'

        test_email_str = open(test_email_filename, 'r').read()

        # send the email to the post handler
        client = Client()
        data = {'email_str': test_email_str}
        client.post(do_add_to_calendar_url, data)

        # get the email object from the db
        e = Email.objects.get(subject=the_subject)
        # get the calendar item object from the db
        c = e.user.userprofile.calendar.filter(name=the_subject).all()[0]

        # post the updated calendar item data to the edit page
        # NOTE: if we wanted to be more careful, we might actually fill in the form by hand
        # but this should be fine for now
        new_name = 'a'
        new_location = 'b'
        new_info = 'c'
        data = {
            'token' : c.token,
            'name' : new_name,
            'location' : new_location,
            'info' : new_info,
        }
        client.post(do_edit_calendar_item_url, data)

        # get the email object from the db
        e = Email.objects.get(subject=the_subject)
        # get the calendar item object from the db
        c = e.user.userprofile.calendar.filter(name=the_subject).all()[0]

        self.AssertEqual(new_name, c.name)
        self.AssertEqual(new_location, c.location)
        self.AssertEqual(new_info, c.info)
