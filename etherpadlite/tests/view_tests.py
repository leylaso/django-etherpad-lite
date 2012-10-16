# ~ endocing: utf-8 ~
from django.core.urlresolvers import reverse
from django.test import TestCase

from etherpadlite.tests.utils import *
from etherpadlite.models import *
import etherpadlite.models

etherpadlite.models.EtherpadLiteClient = EtherpadLiteClientMock


class EtherpadLiteViewsTests(TestCase):

    def setUp(self):
        self.server = PadServer.objects.create(
            title=testserver['title'],
            url=testserver['url'],
            apikey=testserver['apikey']
        )

        self.user = User.objects.create(username='Obi Wan Kenobi')
        self.user.set_password('lightsaber')
        self.user.save()

        self.group = Group.objects.create(name='Jedi')
        self.padGroup = PadGroup.objects.create(
            group=self.group,
            server=self.server
        )
        self.user.groups.add(self.group)

    def test_profile_view(self):
        """ This view is only viewable if you are logged in. So, it should
        redirect to the loginpage (Statuscode 302). Otherwise it returns 200.
        """

        response = self.client.get(reverse('etherpadlite_profile'))
        self.assertEqual(response.status_code, 302)

        self.client.login(username="Obi Wan Kenobi", password="lightsaber")
        response = self.client.get(reverse('etherpadlite_profile'))
        self.assertEqual(response.status_code, 200)

    def test_group_create_view(self):
        """ This view is only viewable if you are logged in. So, it should
        redirect to the loginpage (Statuscode 302). Otherwise it returns 200.

        After verifying this works well, lets try to create a group that
        allready exist, followed by a new group.
        """
        response = self.client.get(reverse('etherpadlite_create_group'))
        self.assertEqual(response.status_code, 302)

        self.client.login(username="Obi Wan Kenobi", password="lightsaber")
        response = self.client.get(reverse('etherpadlite_create_group'))
        self.assertEqual(response.status_code, 200)

        reponse = self.client.post(
            reverse('etherpadlite_create_group'),
            {
                'name': 'Jedi'
            }
        )
        self.assertEqual(reponse.status_code, 200)

        reponse = self.client.post(
            reverse('etherpadlite_create_group'),
            {
                'name': 'Sith'
            }
        )
        self.assertEqual(reponse.status_code, 302)

    def test_group_delete(self):
        """ This view is only viewable if you are logged in. So, it should
        redirect to the loginpage (Statuscode 302). Otherwise it returns 200.

        The User can't delete a group if he is not moderator of the specific
        group.
        """
        pk = self.group.id
        response = self.client.get(
            reverse('etherpadlite_delete_group', kwargs={'pk': pk})
        )
        self.assertEqual(response.status_code, 302)

        self.client.login(username="Obi Wan Kenobi", password="lightsaber")
        response = self.client.get(
            reverse('etherpadlite_delete_group', kwargs={'pk': pk})
        )
        self.assertEqual(response.status_code, 403)

        self.padGroup.moderators.add(self.user)
        response = self.client.get(
            reverse('etherpadlite_delete_group', kwargs={'pk': pk})
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            reverse('etherpadlite_delete_group', kwargs={'pk': pk}),
            {'confirm': ''}
        )
        self.assertEqual(response.status_code, 302)

    def test_group_manage(self):
        """ This view is only viewable if you are logged in. So, it should
        redirect to the loginpage (Statuscode 302). Otherwise it returns 200.

        The User can't manage a group if he is not moderator of the specific
        group. This view is able to add and remove userer to group. It also can
        remove add or remove a moderator. If no moderator is set, the actual
        user should become a modertor.
        """
        pk = self.group.id
        response = self.client.get(
            reverse('etherpadlite_manage_group', kwargs={'pk': pk})
        )
        self.assertEqual(response.status_code, 302)

        self.client.login(username="Obi Wan Kenobi", password="lightsaber")
        response = self.client.get(
            reverse('etherpadlite_manage_group', kwargs={'pk': pk})
        )
        self.assertEqual(response.status_code, 403)

        self.padGroup.moderators.add(self.user)
        response = self.client.get(
            reverse('etherpadlite_manage_group', kwargs={'pk': pk})
        )
        self.assertEqual(response.status_code, 200)

        user2 = User.objects.create(username="Darth Maul")
        user2.save()
        self.client.post(
            reverse('etherpadlite_manage_group', kwargs={'pk': pk}),
            {'userToAdd': "Darth Maul"}
        )
        user_list = self.group.user_set.all()
        self.assertTrue(self.user in user_list and user2 in user_list)
        # Now lets try to add a not existing user
        self.client.post(
            reverse('etherpadlite_manage_group', kwargs={'pk': pk}),
            {'userToAdd': "Qui Gon Jinn"}
        )
        user_list = self.group.user_set.all()
        self.assertTrue(len(user_list) == 2 and self.user in user_list and
            user2 in user_list)

        # Add the user2 to the moderators
        self.client.post(
            reverse('etherpadlite_manage_group', kwargs={'pk': pk}),
            {'isModerator': ["Darth Maul", "Obi Wan Kenobi"]}
        )
        moderators = self.padGroup.moderators.all()
        self.assertTrue(self.user in moderators and user2 in moderators)
        # If we now remove the fist user from the moderators list, we should not
        # be able to access the page anymore.
        response = self.client.post(
            reverse('etherpadlite_manage_group', kwargs={'pk': pk}),
            {'isModerator': ["Darth Maul"]}
        )
        self.assertEqual(response.status_code, 403)
        # Lets try to remove the moderator status from all users. The active
        # user should automaticly bekomm a moderator again.
        self.padGroup.moderators = [self.user]
        self.client.post(
            reverse('etherpadlite_manage_group', kwargs={'pk': pk}),
            {'isModerator': []}
        )
        self.assertTrue(self.user in self.padGroup.moderators.all())
        # Finally lets remove a user from the group.
        self.assertTrue(len(self.group.user_set.all()) == 2 and
            self.user in user_list and
            user2 in user_list)
        self.client.post(
            reverse('etherpadlite_manage_group', kwargs={'pk': pk}),
            {'userToRemove': ["Darth Maul"]}
        )
        self.assertTrue(len(self.group.user_set.all()) == 1 and
            self.user in self.group.user_set.all())

    def test_pad_create_view(self):
        """
        """
        pk = self.group.id
        response = self.client.get(
            reverse('etherpadlite_create_pad', kwargs={'pk': pk})
        )
        self.assertEqual(response.status_code, 302)

        self.client.login(username="Obi Wan Kenobi", password="lightsaber")
        response = self.client.get(
            reverse('etherpadlite_create_pad', kwargs={'pk': pk})
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            reverse('etherpadlite_create_pad', kwargs={'pk': pk}),
            {'name': 'Testpad', 'group': self.group.name}
        )
        self.assertTrue(Pad.objects.get(name="Testpad") in
            self.padGroup.pad_set.all())

    def test_pad_delete_view(self):
        """
        """
        test_pad = Pad.objects.create(
            server=self.server,
            group=self.padGroup,
            name="Testpad"
        )
        test_pad.save()
        response = self.client.get(
            reverse('etherpadlite_delete_pad', kwargs={'pk': test_pad.id})
        )
        self.assertEqual(response.status_code, 302)

        self.client.login(username="Obi Wan Kenobi", password="lightsaber")
        response = self.client.get(
            reverse('etherpadlite_delete_pad', kwargs={'pk': test_pad.id})
        )
        self.assertEqual(response.status_code, 403)

        self.padGroup.moderators.add(self.user)
        response = self.client.get(
            reverse('etherpadlite_delete_pad', kwargs={'pk': test_pad.id})
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            reverse('etherpadlite_delete_pad', kwargs={'pk': test_pad.id}),
            {'confirm': ''}
        )
        self.assertTrue(self.padGroup.pad_set.count() == 0)

    def test_pad_view(self):
        """
        """

    def tearDown(self):
        self.server.delete()
