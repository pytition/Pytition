from django.test import TestCase
from django.urls import reverse

class AllPetitionsViewTest(TestCase):
    """Test all_petitions view"""

    def test_allPetitionsOk(self):
        response = self.client.get(reverse('all_petitions'))
        self.assertEqual(response.status_code, 200)