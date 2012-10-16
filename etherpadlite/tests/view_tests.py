# ~ endocing: utf-8 ~
from django.core.urlresolvers import reverse
from django.test import TestCase

from etherpadlite.models import *
from etherpadlite.tests.utils import *

etherpadlite.models.EtherpadLiteClient = EtherpadLiteClientMock


class EtherpadLiteViewsTests(TestCase):

    def setUp(self):
        self.server = PadServer.objects.create(
            title=testserver['title'],
            url=testserver['url'],
            apikey=testserver['apikey']
        )

    def test_profile_view(self):


    def tearDown(self):
        self.server.delete()
