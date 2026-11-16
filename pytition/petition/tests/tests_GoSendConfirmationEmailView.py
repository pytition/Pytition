
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from .utils import add_default_data

from petition.models import Organization, Petition, Signature, PytitionUser


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

    def test_GoSendConfirmationEmailViewCrossPetitionKO(self):
        # A user must not be able to re-send the confirmation email of a
        # signature belonging to another user's petition.
        self.login('julia')
        max = PytitionUser.objects.get(user__username='max')
        petition = max.petition_set.first()
        data = {
            'first_name': 'Alan',
            'last_name': 'John',
            'email': 'alan@john.org',
            'subscribed_to_mailinglist': False,
        }
        response = self.client.post(reverse('create_signature', args=[petition.id]), data, follow=True)
        signature = Signature.objects.filter(petition=petition).first()
        outbox_before = len(mail.outbox)
        response = self.client.get(reverse('resend_confirmation_email', args=[signature.id]), follow=True)
        self.assertRedirects(response, reverse("user_dashboard"))
        # No confirmation email must have been re-sent to the other user's signer
        self.assertEqual(len(mail.outbox), outbox_before)

    def test_GoSendConfirmationEmailViewOwnerOK(self):
        # The owner of a user petition can re-send the confirmation email of
        # its own signatures.
        julia = self.login('julia')
        petition = julia.petition_set.first()
        data = {
            'first_name': 'Alan',
            'last_name': 'John',
            'email': 'alan@john.org',
            'subscribed_to_mailinglist': False,
        }
        response = self.client.post(reverse('create_signature', args=[petition.id]), data, follow=True)
        signature = Signature.objects.filter(petition=petition).first()
        outbox_before = len(mail.outbox)
        response = self.client.get(reverse('resend_confirmation_email', args=[signature.id]), follow=True)
        self.assertRedirects(response, reverse("user_dashboard"))
        # A confirmation email must have been re-sent to the signer
        self.assertEqual(len(mail.outbox), outbox_before + 1)

    def test_GoSendConfirmationEmailViewOrgAdminOK(self):
        # An admin of the petition's organization can re-send the
        # confirmation email of its signatures.
        self.login('julia')
        org = Organization.objects.get(name='Les Amis de la Terre')
        petition = org.petition_set.first()
        data = {
            'first_name': 'Alan',
            'last_name': 'John',
            'email': 'alan@john.org',
            'subscribed_to_mailinglist': False,
        }
        response = self.client.post(reverse('create_signature', args=[petition.id]), data, follow=True)
        signature = Signature.objects.filter(petition=petition).first()
        outbox_before = len(mail.outbox)
        response = self.client.get(reverse('resend_confirmation_email', args=[signature.id]), follow=True)
        self.assertRedirects(response, reverse("org_dashboard", args=[org.slugname]))
        # A confirmation email must have been re-sent to the signer
        self.assertEqual(len(mail.outbox), outbox_before + 1)

    def test_GoSendConfirmationEmailViewCrossPetitionOrgKO(self):
        # A user who is not a member of the petition's organization must not
        # be able to re-send the confirmation email of its signatures.
        self.login('sarah')
        org = Organization.objects.get(name='Greenpeace')
        petition = org.petition_set.first()
        data = {
            'first_name': 'Alan',
            'last_name': 'John',
            'email': 'alan@john.org',
            'subscribed_to_mailinglist': False,
        }
        response = self.client.post(reverse('create_signature', args=[petition.id]), data, follow=True)
        signature = Signature.objects.filter(petition=petition).first()
        outbox_before = len(mail.outbox)
        response = self.client.get(reverse('resend_confirmation_email', args=[signature.id]), follow=True)
        self.assertRedirects(response, reverse("user_dashboard"))
        # No confirmation email must have been re-sent to the signer
        self.assertEqual(len(mail.outbox), outbox_before)
