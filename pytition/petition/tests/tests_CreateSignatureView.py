from django.test import TestCase
from django.urls import reverse

from .utils import add_default_data

from petition.models import Petition, Signature


class CreateSignatureViewTest(TestCase):
    """Test create_signature view"""

    @classmethod
    def setUpTestData(cls):
        add_default_data()

    def test_CreateSignaturePOSTOk(self):
        data = {
            'first_name': 'Alan',
            'last_name': 'John',
            'email': 'alan@john.org',
            'phone': '0605040302',
            'subscribed_to_mailinglist': False,
        }
        petition = Petition.objects.filter(published=True).first()
        response = self.client.post(reverse('create_signature', args=[petition.id]), data, follow=True)
        self.assertRedirects(response, petition.url)
        signature = Signature.objects.filter(petition=petition).first()
        self.assertEqual(signature.confirmed, False)
        self.assertEqual(signature.email, 'alan@john.org')
        self.assertEqual(signature.phone, '+33605040302')
        self.assertEqual(signature.first_name, 'Alan')
        self.assertEqual(signature.last_name, 'John')
        self.assertEqual(signature.subscribed_to_mailinglist, False)

    def test_CreateSignaturePOSTNok(self):
        data = {
            'first_name': 'Alan',
            'last_name': '',
            'email': 'wrong-mail.org',
            'phone': '060504030201',
        }
        petition = Petition.objects.filter(published=True).first()
        response = self.client.post(reverse('create_signature', args=[petition.id]), data)
        self.assertEqual(Signature.objects.count(), 0)
        self.assertTemplateUsed(response, 'petition/petition_detail.html')
        self.assertContains(response, 'This field is required')
        self.assertContains(response, 'Enter a valid phone number')
        self.assertContains(response, 'Enter a valid email address')

    def test_CreateSignatureGETOk(self):
        petition = Petition.objects.filter(published=True).first()
        response = self.client.get(reverse('create_signature', args=[petition.id]), follow=True)
        self.assertRedirects(response, petition.url)
