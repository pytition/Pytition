from django.test import TestCase
from django.urls import reverse

class SearchViewTest(TestCase):
    """Test search view"""

    def test_SearchOk(self):
        """
        Returns the search results.

        Args:
            self: (todo): write your description
        """
        response = self.client.get(reverse('search'))
        self.assertEqual(response.status_code, 200)

    def test_SearchWithQueryOk(self):
        """
        Returns the search for a search result.

        Args:
            self: (todo): write your description
        """
        response = self.client.get(reverse('search')+"?q=petition")
        self.assertEqual(response.status_code, 200)