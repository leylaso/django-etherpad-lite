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
        """ Tests for the profile view.
        """
        import pdb;pdb.set_trace()
        response = self.client.get(reverse('etherpadlite_profile'))
        self.assertEqual(response.status_code, 302)

        self.client.login(username="Obi Wan Kenobi", password="lightsaber")
        response = self.client.get(reverse('etherpadlite_profile'))
        self.assertEqual(response.status_code, 200)

    def test_group_create_view(self):
        """ Tests for group creation view.
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
        """ Tests for group deletion view.
        """
        slug = self.padGroup.slug
        response = self.client.get(
            reverse('etherpadlite_delete_group', kwargs={'slug': slug})
        )
        self.assertEqual(response.status_code, 302)

        self.client.login(username="Obi Wan Kenobi", password="lightsaber")
        response = self.client.get(
            reverse('etherpadlite_delete_group', kwargs={'slug': slug})
        )
        self.assertEqual(response.status_code, 403)

        self.padGroup.moderators.add(self.user)
        response = self.client.get(
            reverse('etherpadlite_delete_group', kwargs={'slug': slug})
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            reverse('etherpadlite_delete_group', kwargs={'slug': slug}),
            {'confirm': ''}
        )
        self.assertEqual(response.status_code, 302)

    def test_group_manage(self):
        """ Tests for group manage view.
        """
        slug = self.padGroup.slug
        response = self.client.get(
            reverse('etherpadlite_manage_group', kwargs={'slug': slug})
        )
        self.assertEqual(response.status_code, 302)

        self.client.login(username="Obi Wan Kenobi", password="lightsaber")
        response = self.client.get(
            reverse('etherpadlite_manage_group', kwargs={'slug': slug})
        )
        self.assertEqual(response.status_code, 403)

        self.padGroup.moderators.add(self.user)
        response = self.client.get(
            reverse('etherpadlite_manage_group', kwargs={'slug': slug})
        )
        self.assertEqual(response.status_code, 200)

        user2 = User.objects.create(username="Darth Maul")
        user2.save()
        self.client.post(
            reverse('etherpadlite_manage_group', kwargs={'slug': slug}),
            {'userToAdd': "Darth Maul"}
        )
        user_list = self.group.user_set.all()
        self.assertTrue(self.user in user_list and user2 in user_list)
        # Now lets try to add a not existing user
        self.client.post(
            reverse('etherpadlite_manage_group', kwargs={'slug': slug}),
            {'userToAdd': "Qui Gon Jinn"}
        )
        user_list = self.group.user_set.all()
        self.assertTrue(len(user_list) == 2 and self.user in user_list and
            user2 in user_list)

        # Add the user2 to the moderators
        self.client.post(
            reverse('etherpadlite_manage_group', kwargs={'slug': slug}),
            {'isModerator': ["Darth Maul", "Obi Wan Kenobi"]}
        )
        moderators = self.padGroup.moderators.all()
        self.assertTrue(self.user in moderators and user2 in moderators)
        # If we now remove the fist user from the moderators list, we should not
        # be able to access the page anymore.
        response = self.client.post(
            reverse('etherpadlite_manage_group', kwargs={'slug': slug}),
            {'isModerator': ["Darth Maul"]}
        )
        self.assertEqual(response.status_code, 403)
        # Lets try to remove the moderator status from all users. The active
        # user should automaticly bekomm a moderator again.
        self.padGroup.moderators = [self.user]
        self.client.post(
            reverse('etherpadlite_manage_group', kwargs={'slug': slug}),
            {'isModerator': []}
        )
        self.assertTrue(self.user in self.padGroup.moderators.all())
        # Finally lets remove a user from the group.
        self.assertTrue(len(self.group.user_set.all()) == 2 and
            self.user in user_list and
            user2 in user_list)
        self.client.post(
            reverse('etherpadlite_manage_group', kwargs={'slug': slug}),
            {'userToRemove': ["Darth Maul"]}
        )
        self.assertTrue(len(self.group.user_set.all()) == 1 and
            self.user in self.group.user_set.all())

    def test_pad_create_view(self):
        """ Tests for pad create view.
        """
        slug = self.padGroup.slug
        response = self.client.get(
            reverse('etherpadlite_create_pad', kwargs={'slug': slug})
        )
        self.assertEqual(response.status_code, 302)

        self.client.login(username="Obi Wan Kenobi", password="lightsaber")
        response = self.client.get(
            reverse('etherpadlite_create_pad', kwargs={'slug': slug})
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            reverse('etherpadlite_create_pad', kwargs={'slug': slug}),
            {'name': 'Testpad', 'group': self.group.name}
        )
        self.assertTrue(Pad.objects.get(name="Testpad") in
            self.padGroup.pad_set.all())

    def test_pad_delete_view(self):
        """ Tests for pad delete view.
        """
        test_pad = Pad.objects.create(
            server=self.server,
            group=self.padGroup,
            name="Testpad"
        )
        test_pad.save()
        response = self.client.get(
            reverse('etherpadlite_delete_pad', kwargs={'pad_slug': test_pad.slug, 'group_slug': self.padGroup.slug})
        )
        self.assertEqual(response.status_code, 302)

        self.client.login(username="Obi Wan Kenobi", password="lightsaber")
        response = self.client.get(
            reverse('etherpadlite_delete_pad', kwargs={'pad_slug': test_pad.slug, 'group_slug': self.padGroup.slug})
        )
        self.assertEqual(response.status_code, 403)

        self.padGroup.moderators.add(self.user)
        response = self.client.get(
            reverse('etherpadlite_delete_pad', kwargs={'pad_slug': test_pad.slug, 'group_slug': self.padGroup.slug})
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            reverse('etherpadlite_delete_pad', kwargs={'pad_slug': test_pad.slug, 'group_slug': self.padGroup.slug}),
            {'confirm': ''}
        )
        self.assertTrue(self.padGroup.pad_set.count() == 0)

    def test_pad_view(self):
        """ Tests for Pad view.
        """
        self.author = PadAuthor.objects.create(
            user=self.user,
            server=self.server
        )
        test_pad = Pad.objects.create(
            server=self.server,
            group=self.padGroup,
            name="Testpad"
        )
        test_pad.save()
        response = self.client.get(
            reverse('etherpadlite_view_pad', kwargs={
                'pad_slug': test_pad.slug, 'group_slug': self.padGroup.slug
            })
        )
        self.assertEqual(response.status_code, 302)

        self.client.login(username="Obi Wan Kenobi", password="lightsaber")
        response = self.client.get(
            reverse('etherpadlite_view_pad', kwargs={
                'pad_slug': test_pad.slug, 'group_slug': self.padGroup.slug
            })
        )
        self.assertEqual(response.status_code, 200)

        self.padGroup.authors.add(self.author)
        response = self.client.get(
            reverse('etherpadlite_view_pad', kwargs={
                'pad_slug': test_pad.slug, 'group_slug': self.padGroup.slug
            })
        )
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        self.server.delete()
