from django.test import TestCase
from django.urls import reverse

from .utils import add_default_data

from petition.models import PytitionUser, Permission, Organization


class OrgDeleteMemberViewTest(TestCase):
    """Test org_delete_member view"""

    @classmethod
    def setUpTestData(cls):
        add_default_data()

    def login(self, name, password=None):
        self.client.login(username=name, password=password if password else name)
        self.pu = PytitionUser.objects.get(user__username=name)
        return self.pu

    def logout(self):
        self.client.logout()

    def test_OrgDeleteMemberViewOk(self):
        """Let's try to add and then delete user max to org RAP"""
        # Add max to RAP
        julia = self.login('julia')
        julia_perms = Permission.objects.get(organization__slugname="rap", user=julia)
        julia_perms.can_add_members = True
        # Add permission to remove members
        julia_perms.can_remove_members = True
        julia_perms.save()
        response = self.client.get(reverse('org_add_user', args=["rap"])+"?user=max")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        user = PytitionUser.objects.get(user__username='max')
        rap = Organization.objects.get(slugname='rap')
        invitations = user.invitations.all()
        self.assertIn(rap, invitations)
        # Max accepts invitation
        self.logout()
        max = self.login("max")
        response = self.client.get(reverse('invite_accept', kwargs={'orgslugname': 'rap'}), follow=True)
        self.assertRedirects(response, reverse("user_dashboard"))
        rap = Organization.objects.get(slugname="rap")
        self.assertIn(max, rap.members.all())
        self.assertIn(rap, max.organization_set.all())
        self.assertNotIn(rap, max.invitations.all())
        # Remove max from RAP
        self.logout()
        julia = self.login("julia")
        response = self.client.get(reverse('org_delete_member', kwargs={'orgslugname': 'rap'}) + "?member=max")
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response["Content-Type"], "application/json")


    def test_OrgDeleteMemberViewKoForbidden(self):
        """Let's try to add user max to org RAP from non-authorized Julia user"""
        # Add max to RAP
        julia = self.login('julia')
        julia_perms = Permission.objects.get(organization__slugname="rap", user=julia)
        julia_perms.can_add_members = True
        julia_perms.can_remove_members = False
        julia_perms.save()
        response = self.client.get(reverse('org_add_user', args=["rap"])+"?user=max")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        user = PytitionUser.objects.get(user__username='max')
        rap = Organization.objects.get(slugname='rap')
        invitations = user.invitations.all()
        self.assertIn(rap, invitations)
        # Max accepts invitation
        self.logout()
        max = self.login("max")
        response = self.client.get(reverse('invite_accept', kwargs={'orgslugname': 'rap'}), follow=True)
        self.assertRedirects(response, reverse("user_dashboard"))
        rap = Organization.objects.get(slugname="rap")
        self.assertIn(max, rap.members.all())
        self.assertIn(rap, max.organization_set.all())
        self.assertNotIn(rap, max.invitations.all())
        # Remove max from RAP
        self.logout()
        julia = self.login("julia")
        # Now try to remove member from RAP org without the corresponding permission
        response = self.client.get(reverse('org_delete_member', args=["rap"])+"?member=max")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_OrgDeleteMemberLastAdminKo(self):
        julia = self.login('julia')
        julia_perms = Permission.objects.get(organization__slugname="rap", user=julia)
        # Add permission to remove members
        julia_perms.can_remove_members = True
        julia_perms.save()
        response = self.client.get(reverse('org_delete_member', kwargs={'orgslugname': 'rap'}) + "?member=julia")
        self.assertEquals(response.status_code, 403)
        self.assertEquals(response["Content-Type"], "application/json")
