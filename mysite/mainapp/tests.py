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
    def test_email_adding_to_db(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        c = Client()
        test_email_filename = 'mainapp/test_data/sample_msg.email'
        the_subject = 'yo dog'
        the_body = 'asdfsadf'

        email_str = open(test_email_filename, 'r').read()
        data = {'email_str': email_str}
        c.post('/add/email', data)
        e = Email.objects.get(subject=the_subject)
        self.failUnlessEqual(e.body, the_body)

__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}

