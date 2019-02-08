from django.test import TestCase
from petition.models import Organization, Petition


class ViewsTest(TestCase):
    """Test views"""
    @classmethod
    def setUpTestData(cls):
        petitions_nb = 9
        for i in range(petitions_nb):
            p = Petition.objects.create(title="Petition {i}", text=f"blabla {i}", published=True)

    def tearDown(self):
        # Clean up run after every test method.
        pass

    def test_index_200(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_petition_list(self):
        response = self.client.get('/')
        self.assertTrue(len(response.context['petitions']) == 9)
