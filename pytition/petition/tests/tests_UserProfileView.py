from django.test import TestCase
from django.urls import reverse

from .utils import add_default_data


class UserProfileViewTest(TestCase):
    """Test user_profile view"""

    @classmethod
    def setUpTestData(cls):
        """
        Sets the default data set.

        Args:
            cls: (todo): write your description
        """
        add_default_data()

    def test_UserProfileViewOk(self):
        """
        Method to see if user is logged in.

        Args:
            self: (todo): write your description
        """
        response = self.client.get(reverse('user_profile', args=["max"]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "petition/user_profile.html")

    def test_UserProfileViewKo(self):
        """
        Method to see if the user when the user is logged.

        Args:
            self: (todo): write your description
        """
        response = self.client.get(reverse('user_profile', args=["not_existing_user"]))
        self.assertEqual(response.status_code, 404)
