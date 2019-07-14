from django.test import TestCase
from django.urls import reverse

from .utils import add_default_data

from petition.models import PytitionUser, Permission, Organization


class OrgAddUserViewTest(TestCase):
    """Test org_add_user view"""

    @classmethod
    def setUpTestData(cls):
        add_default_data()

    def login(self, name, password=None):
        self.client.login(username=name, password=password if password else name)
        self.pu = PytitionUser.objects.get(user__username=name)
        return self.pu

    def test_OrgAddUserViewOk(self):
        """Let's try to add user max to org RAP"""
        julia = self.login('julia')
        response = self.client.get(reverse('org_add_user', args=["rap"])+"?user=max")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        user = PytitionUser.objects.get(user__username='max')
        rap = Organization.objects.get(slugname='rap')
        invitations = user.invitations.all()
        self.assertIn(rap, invitations)

    def test_OrgAddUserViewKoForbidden(self):
        """Let's try to add user max to org RAP from non-authorized users"""
        # John is not in RAP org
        self.login('john')
        response = self.client.get(reverse('org_add_user', args=["rap"])+"?user=max")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response['Content-Type'], 'application/json')
        # Max is in "Les Amis de la Terre" but does not have "add member" right
        self.login("max")
        org = Organization.objects.get(name="Les Amis de la Terre")
        response = self.client.get(reverse('org_add_user', args=[org.slugname])+"?user=john")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response['Content-Type'], 'application/json')
        # Try to add someone already in the Org
        self.login("julia")
        response = self.client.get(reverse('org_add_user', args=[org.slugname]) + "?user=max")
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response['Content-Type'], 'application/json')