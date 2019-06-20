from django.test import TestCase
from django.urls import reverse

from .utils import add_default_data


class OrgProfileViewTest(TestCase):
    """Test org_profile view"""

    @classmethod
    def setUpTestData(cls):
        add_default_data()

    def test_OrgProfileViewOk(self):
        response = self.client.get(reverse('org_profile', args=["rap"]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "petition/org_profile.html")

    def test_OrgProfileViewKo(self):
        response = self.client.get(reverse('org_profile', args=["not_existing_org"]))
        self.assertEqual(response.status_code, 404)
