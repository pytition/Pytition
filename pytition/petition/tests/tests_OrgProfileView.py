from django.test import TestCase
from django.urls import reverse

from .utils import add_default_data


class OrgProfileViewTest(TestCase):
    """Test org_profile view"""

    @classmethod
    def setUpTestData(cls):
        """
        Sets the default data set.

        Args:
            cls: (todo): write your description
        """
        add_default_data()

    def test_OrgProfileViewOk(self):
        """
        Respond to the currently selected outline.

        Args:
            self: (todo): write your description
        """
        response = self.client.get(reverse('org_profile', args=["rap"]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "petition/org_profile.html")

    def test_OrgProfileViewKo(self):
        """
        Respond to the currently selected tests.

        Args:
            self: (todo): write your description
        """
        response = self.client.get(reverse('org_profile', args=["not_existing_org"]))
        self.assertEqual(response.status_code, 404)
