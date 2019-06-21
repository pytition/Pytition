from django.test import TestCase
from django.urls import reverse

from .utils import add_default_data

from petition.models import PytitionUser, Permission, Organization


class InviteDismissViewTest(TestCase):
    """Test invite_dismiss view"""

    @classmethod
    def setUpTestData(cls):
        add_default_data()

    def login(self, name, password=None):
        self.client.login(username=name, password=password if password else name)
        self.pu = PytitionUser.objects.get(user__username=name)
        return self.pu

    def logout(self):
        self.client.logout()

    def test_InviteDismissViewOk(self):
        julia = self.login("julia")
        # julia invites max
        julia_perms = Permission.objects.get(organization__slugname="rap", user=julia)
        julia_perms.can_add_members = True
        julia_perms.save()
        response = self.client.get(reverse('org_add_user', args=["rap"])+"?user=max")
        self.assertEqual(response.status_code, 200)
        self.logout()
        max = self.login("max")
        # max dismisses julia's invitation
        response = self.client.get(reverse('invite_dismiss', kwargs={'orgslugname': 'rap'}), follow=True)
        self.assertRedirects(response, reverse("user_dashboard"))
        rap = Organization.objects.get(slugname="rap")
        self.assertNotIn(max, rap.members.all())
        self.assertNotIn(rap, max.organization_set.all())
        self.assertNotIn(rap, max.invitations.all())