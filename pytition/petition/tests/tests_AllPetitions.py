from django.test import TestCase
from django.urls import reverse

class AllPetitionsViewTest(TestCase):
    """Test all_petitions view"""

    def test_allPetitionsOk(self):
        """
        Test if all test test jobs.

        Args:
            self: (todo): write your description
        """
        response = self.client.get(reverse('all_petitions'))
        self.assertEqual(response.status_code, 302)
