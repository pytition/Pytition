from django.test import TestCase
from django.urls import reverse

from .utils import add_default_data

from petition.models import Petition

class DetailViewTest(TestCase):
    """Test detail view"""

    @classmethod
    def setUpTestData(cls):
        """
        Sets the default data set.

        Args:
            cls: (todo): write your description
        """
        add_default_data()

    def test_DetailOk(self):
        """
        Test if a single document

        Args:
            self: (todo): write your description
        """
        petition = Petition.objects.filter(published=True).first()
        response = self.client.get(reverse('detail', args=[petition.id]))
        self.assertEqual(response.status_code, 200)