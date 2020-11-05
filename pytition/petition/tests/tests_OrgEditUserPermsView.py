from django.test import TestCase
from django.urls import reverse

from .utils import add_default_data

from petition.models import PytitionUser, Permission, Organization


class OrgEditUserPermsViewTest(TestCase):
    """Test org_edit_user_perms view"""

    @classmethod
    def setUpTestData(cls):
        """
        Sets the default data set.

        Args:
            cls: (todo): write your description
        """
        add_default_data()

    def login(self, name, password=None):
        """
        Login with the given credentials.

        Args:
            self: (todo): write your description
            name: (str): write your description
            password: (str): write your description
        """
        self.client.login(username=name, password=password if password else name)
        self.pu = PytitionUser.objects.get(user__username=name)
        return self.pu

    def logout(self):
        """
        Logout of the client.

        Args:
            self: (todo): write your description
        """
        self.client.logout()

    def test_OrgEditUserPermsViewOk(self):
        """
        This method is called when the user is allowed.

        Args:
            self: (todo): write your description
        """
        julia = self.login("julia")
        response = self.client.get(reverse("org_edit_user_perms", kwargs={'orgslugname': 'rap', 'user_name': 'julia'}))
        self.assertEquals(response.status_code, 200)
