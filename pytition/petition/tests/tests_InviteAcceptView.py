from django.test import TestCase
from django.urls import reverse

from .utils import add_default_data

from petition.models import PytitionUser, Permission, Organization


class InviteAcceptViewTest(TestCase):
    """Test invite_accept view"""

    @classmethod
    def setUpTestData(cls):
        add_default_data()

    def login(self, name, password=None):
        self.client.login(username=name, password=password if password else name)
        self.pu = PytitionUser.objects.get(user__username=name)
        return self.pu

    def logout(self):
        self.client.logout()

    def test_InviteAcceptViewOk(self):
        julia = self.login("julia")
        # julia invites max
        julia_perms = Permission.objects.get(organization__slugname="rap", user=julia)
        julia_perms.can_add_members = True
        julia_perms.save()
        response = self.client.get(reverse('org_add_user', args=["rap"])+"?user=max")
        self.assertEqual(response.status_code, 200)
        self.logout()
        max = self.login("max")
        # max accepts julia's invitation
        response = self.client.get(reverse('invite_accept', kwargs={'orgslugname': 'rap'}), follow=True)
        self.assertRedirects(response, reverse("user_dashboard"))
        rap = Organization.objects.get(slugname="rap")
        self.assertIn(max, rap.members.all())
        self.assertIn(rap, max.organization_set.all())
        self.assertNotIn(rap, max.invitations.all())