from django.test import TestCase
from django.urls import reverse

class SearchViewTest(TestCase):
    """Test search view"""

    def test_SearchOk(self):
        response = self.client.get(reverse('search'))
        self.assertEqual(response.status_code, 200)