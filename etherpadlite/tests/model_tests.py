# ~ encoding: utf-8 ~
from django.test import TestCase
from django.contrib.auth.models import *

from etherpadlite.tests.utils import *
from etherpadlite.models import *
import etherpadlite.models


import string

etherpadlite.models.EtherpadLiteClient = EtherpadLiteClientMock


class PadServerTestCase(TestCase):
    """Test cases for the Server model
    """

    def setUp(self):
        self.server = PadServer.objects.create(
            title=testserver['title'],
            url=testserver['url'],
            apikey=testserver['apikey']
        )

    def testBasics(self):
        self.assertTrue(isinstance(self.server, PadServer))
        self.assertEqual(self.server.__unicode__(), testserver['url'])
        self.assertEqual(self.server.apikey, testserver['apikey'])

    def test_apiurl_property(self):
        """ Test the apiurl property of the Server Model. This property should
        return url with an endling /api no matter the url endet with an / or
        not.
        """
        self.assertEqual(self.server.apiurl, 'http://www.example.com/api')
        # let the url end with a / and and test again...
        self.server.url = '%s/' % testserver['url']
        self.assertEqual(self.server.apiurl, 'http://www.example.com/api')

    def tearDown(self):
        self.server.delete()


class PadGroupTestCase(TestCase):
    """Test cases for the Group model
    """

    def setUp(self):
        self.server = PadServer.objects.create(
            title=testserver['title'],
            url=testserver['url'],
            apikey=testserver['apikey']
        )
        self.group = Group.objects.create(name='Jedi')
        self.padGroup = PadGroup.objects.create(
            group=self.group,
            server=self.server
        )
        self.user_in_group = User.objects.create(username='Obi Wan Kenobi')
        self.user_in_group.groups.add(self.group)
        self.padGroup.moderators.add(self.user_in_group)

        self.user_not_in_group = User.objects.create(username="Darth Maul")

    def testBasics(self):
        self.assertTrue(isinstance(self.padGroup, PadGroup))
        self.assertEqual(self.padGroup.__unicode__(), self.group.__unicode__())
        self.assertEqual(self.padGroup.server, self.server)

    def test_get_random_id(self):
        """ The _get_random_id function returns a random generated id. This
        function accept a size keyword, determining the number of characters
        and a chars keyword to specify what chars are allowed.
        """
        chars = ['A', 'B', 'C', 'a', 'b', 'c', '1', '2', '3']
        generated_id = self.padGroup._get_random_id(size=3, chars=chars)
        # the returned id must have a a len of 3
        self.assertEqual(len(generated_id), 3)
        # every char must be in the committed chars
        for char in generated_id:
            self.assertTrue(char in chars)
        # if no keywordarguments are specified, it should return 6 chars
        generated_id_2 = self.padGroup._get_random_id()
        self.assertEqual(len(generated_id_2), 6)
        # if no keywordarguments are specified, it should return only
        # uppercase assciichars, lowercase assciichars and diggits.
        chars = string.ascii_uppercase + string.digits + string.ascii_lowercase
        for char in generated_id_2:
            self.assertTrue(char in chars)

    def test_is_moderator(self):
        self.assertTrue(self.padGroup.is_moderator(self.user_in_group))
        # Test with a user that is not a moderator
        self.assertFalse(self.padGroup.is_moderator(self.user_not_in_group))

    def tearDown(self):
        self.user_in_group.delete()
        self.user_not_in_group.delete()
        self.group.delete()
        self.server.delete()


class PadAuthorTestCase(TestCase):
    """Test cases for the Author model
    """

    def setUp(self):
        self.server = PadServer.objects.create(
            title=testserver['title'],
            url=testserver['url'],
            apikey=testserver['apikey']
        )
        self.user = User.objects.create(username='Obi Wan Kenobi')
        self.author = PadAuthor.objects.create(
            user=self.user,
            server=self.server
        )
        self.group = Group.objects.create(name='Jedi')
        self.padGroup = PadGroup.objects.create(
            group=self.group,
            server=self.server
        )
        self.user.groups.add(self.group)
        self.padGroup.moderators.add(self.user)

    def testBasics(self):
        self.assertTrue(isinstance(self.author, PadAuthor))
        self.assertEqual(self.author.__unicode__(), self.user.__unicode__())

    def tearDown(self):
        self.user.delete()
        self.group.delete()
        self.padGroup.delete()
        self.server.delete()


class PadTestCase(TestCase):
    """Test cases for the Pad model
    """

    def setUp(self):
        self.server = PadServer.objects.create(
            title=testserver['title'],
            url=testserver['url'],
            apikey=testserver['apikey']
        )
        self.user = User.objects.create(username='Obi Wan Kenobi')
        self.group = Group.objects.create(name='Jedi')
        self.padGroup = PadGroup.objects.create(
            group=self.group,
            server=self.server
        )
        self.author = PadAuthor.objects.create(
            user=self.user,
            server=self.server
        )
        self.pad1 = Pad.objects.create(
            name='R2D2',
            server=self.server,
            group=self.padGroup
        )
        self.pad2 = Pad.objects.create(
            name='C3PO',
            server=self.server,
            group=self.padGroup
        )

    def testBasics(self):
        self.assertTrue(isinstance(self.pad1, Pad))
        self.assertTrue(isinstance(self.pad2, Pad))
        self.assertEqual(self.pad1.__unicode__(), self.pad1.name)
        self.assertEqual(self.pad2.__unicode__(), self.pad2.name)

    def test_isPublic(self):
        """ Pads can be public or closed. We assume, the pad1 is a public pad
        and pad2 is a closed one.
        """
        self.assertTrue(self.pad1.isPublic())
        self.assertFalse(self.pad2.isPublic())

    def test_ReadOnly(self):
        self.pad1.ReadOnly()

    def tearDown(self):
        self.group.delete()
        self.pad1.delete()
        self.pad2.delete()
        self.user.delete()
