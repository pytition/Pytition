
from django.test import TestCase
from django.urls import reverse

from .utils import add_default_data

from petition.models import Petition, Signature, PytitionUser


class GoSendConfirmationEmailViewTest(TestCase):
    """Test go_send_confirmation_email view"""

    @classmethod
    def setUpTestData(cls):
        add_default_data()

    def login(self, name, password=None):
        self.client.login(username=name, password=password if password else name)
        self.pu = PytitionUser.objects.get(user__username=name)
        return self.pu

    def logout(self):
        self.client.logout()

    def test_GoSendConfirmationEmailViewLoginKO(self):
        self.logout()
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
        response = self.client.get(reverse('resend_confirmation_email', args=[signature.id]), follow=True)
        self.assertRedirects(response, reverse("login")+"?next="+reverse("resend_confirmation_email",
                                                                         args=[signature.id]))

    def test_GoSendConfirmationEmailViewLoginOK(self):
        self.login('admin')
        data = {
            'first_name': 'Alan',
            'last_name': 'John',
            'email': 'alan@john.org',
            'subscribed_to_mailinglist': False,
        }
        app_label = Signature._meta.app_label
        petition = Petition.objects.filter(published=True).first()
        response = self.client.post(reverse('create_signature', args=[petition.id]), data, follow=True)
        self.assertRedirects(response, petition.url)
        signature = Signature.objects.filter(petition=petition).first()
        response = self.client.get(reverse('resend_confirmation_email', args=[signature.id]), follow=True)
        self.assertRedirects(response, reverse('admin:{}_signature_change'.format(app_label), args=[signature.id]))
