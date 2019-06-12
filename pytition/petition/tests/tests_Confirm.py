from django.test import TestCase
from django.urls import reverse

from .utils import add_default_data

from petition.models import Petition, Signature

class ConfirmViewTest(TestCase):
    """Test confirm view"""

    @classmethod
    def setUpTestData(cls):
        add_default_data()

    def test_ConfirmOk(self):
        data = {
            'first_name': 'Alan',
            'last_name': 'John',
            'email': 'alan@john.org',
            'subscribed_to_mailinglist': False,
        }
        petition = Petition.objects.filter(published=True).first()
        response = self.client.post(reverse('create_signature', args=[petition.id]), data, follow=True)
        self.assertRedirects(response, petition.url)
        signature = Signature.objects.filter(petition=petition).first()
        self.assertEqual(signature.confirmed, False)
        confirm_hash = signature.confirmation_hash
        response = self.client.get(reverse('confirm', args=[petition.id, confirm_hash]), follow=True)
        self.assertRedirects(response, petition.url)
        signature = Signature.objects.filter(petition=petition).first() # Reload the object
        self.assertEqual(signature.confirmed, True)