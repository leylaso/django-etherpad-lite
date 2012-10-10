"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.utils import unittest
from django.contrib.auth.models import *

from etherpadlite.config import TESTING_SERVER as TS
from etherpadlite.models import *


class PadServerTestCase(unittest.TestCase):
    """Test cases for the Server model
    """

    def setUp(self):
        self.server = PadServer.objects.create(
            title=TS['title'],
            url=TS['url'],
            apikey=TS['apikey']
        )

    def testBasics(self):
        self.assertTrue(isinstance(self.server, PadServer))
        self.assertEqual(self.server.__unicode__(), TS['url'])


class PadGroupTestCase(unittest.TestCase):
    """Test cases for the Group model
    """

    def setUp(self):
        self.server = PadServer.objects.create(
            title=TS['title'],
            url=TS['url'],
            apikey=TS['apikey']
        )
        self.group = Group.objects.create(name='test')
        self.padGroup = PadGroup.objects.create(
            group=self.group,
            server=self.server
        )

    def testBasics(self):
        self.assertTrue(isinstance(self.padGroup, PadGroup))
        self.assertEqual(self.padGroup.__unicode__(), self.group.__unicode__())

    def tearDown(self):
        self.padGroup.delete()


class PadAuthorTestCase(unittest.TestCase):
    """Test cases for the Author model
    """

    def setUp(self):
        self.server = PadServer.objects.create(
            title=TS['title'],
            url=TS['url'],
            apikey=TS['apikey']
        )
        self.user = User.objects.create(username='jdoe')
        self.group = Group.objects.create(name='does')
        self.padGroup = PadGroup.objects.create(
            group=self.group,
            server=self.server
        )
        self.author = PadAuthor.objects.create(
            user=self.user,
            server=self.server
        )

    def testBasics(self):
        self.assertTrue(isinstance(self.author, PadAuthor))
        self.assertEqual(self.author.__unicode__(), self.user.__unicode__())

    def tearDown(self):
        self.padGroup.delete()


class PadTestCase(unittest.TestCase):
    """Test cases for the Pad model
    """

    def setUp(self):
        self.server = PadServer.objects.create(
            title=TS['title'],
            url=TS['url'],
            apikey=TS['apikey']
        )
        self.user = User.objects.create(username='mrx')
        self.group = Group.objects.create(name='anon')
        self.padGroup = PadGroup.objects.create(
            group=self.group,
            server=self.server
        )
        self.author = PadAuthor.objects.create(
            user=self.user,
            server=self.server
        )
        self.pad = Pad.objects.create(
            name='foo',
            server=self.server,
            group=self.padGroup
        )

    def testBasics(self):
        self.assertTrue(isinstance(self.pad, Pad))
        self.assertEqual(self.pad.__unicode__(), self.pad.name)

    def tearDown(self):
        self.padGroup.delete()
        self.pad.delete()
