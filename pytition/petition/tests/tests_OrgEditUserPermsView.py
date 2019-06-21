from django.test import TestCase
from django.urls import reverse

from .utils import add_default_data

from petition.models import PytitionUser, Permission, Organization


class OrgEditUserPermsViewTest(TestCase):
    """Test org_edit_user_perms view"""

    @classmethod
    def setUpTestData(cls):
        add_default_data()

    def login(self, name, password=None):
        self.client.login(username=name, password=password if password else name)
        self.pu = PytitionUser.objects.get(user__username=name)
        return self.pu

    def logout(self):
        self.client.logout()

    def test_OrgEditUserPermsViewOk(self):
        julia = self.login("julia")
        response = self.client.get(reverse("org_edit_user_perms", kwargs={'orgslugname': 'rap', 'user_name': 'julia'}))
        self.assertEquals(response.status_code, 200)
