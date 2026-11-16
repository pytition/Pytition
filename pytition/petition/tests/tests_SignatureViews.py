from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import constants

from petition.models import Organization, Petition, PytitionUser, Signature, Permission
from .utils import add_default_data


class PetitionViewTest(TestCase):
    """Test index view"""
    @classmethod
    def setUpTestData(cls):
        add_default_data()

    def tearDown(self):
        # Clean up run after every test method.
        pass

    def login(self, name, password=None):
        self.client.login(username=name, password=password if password else name)
        self.pu = PytitionUser.objects.get(user__username=name)
        return self.pu

    def logout(self):
        self.client.logout()

    def test_show_signatures(self):
        julia = self.login('julia')
        # User petition
        p = julia.petition_set.first()
        response = self.client.get(reverse("show_signatures", args=[p.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "petition/signature_data.html")
        # Add signature
        self.assertEqual(Signature.objects.count(), 0)
        Signature.objects.create(
                first_name="Me",
                last_name="You",
                email="you@example.org",
                petition = p)
        self.assertEqual(Signature.objects.count(), 1)
        response = self.client.get(reverse("show_signatures", args=[p.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "petition/signature_data.html")
        # Org petition
        max = self.login("max")
        org = Organization.objects.get(name='Les Amis de la Terre')
        p2 = org.petition_set.first()
        response = self.client.get(reverse("show_signatures", args=[p2.id]))
        self.assertEqual(response.status_code, 302)
        # Ah right, Max does not have access rights for that
        perm = Permission.objects.get(organization=org, user=max)
        perm.can_view_signatures = True
        perm.save()
        response = self.client.get(reverse("show_signatures", args=[p2.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "petition/signature_data.html")

    def test_get_csv_signature(self):
        julia = self.login('julia')
        # User petition
        p = julia.petition_set.first()
        response = self.client.get(reverse("get_csv_signature", args=[p.id]))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("get_csv_confirmed_signature", args=[p.id]))
        self.assertEqual(response.status_code, 200)
        # Add signature
        self.assertEqual(Signature.objects.count(), 0)
        Signature.objects.create(
                first_name="Me",
                last_name="You",
                email="you@example.org",
                petition = p)
        self.assertEqual(Signature.objects.count(), 1)
        response = self.client.get(reverse("get_csv_signature", args=[p.id]))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("get_csv_confirmed_signature", args=[p.id]))
        self.assertEqual(response.status_code, 200)
        # Org petition
        self.login("max")
        org = Organization.objects.get(name='Les Amis de la Terre')
        p2 = org.petition_set.first()
        response = self.client.get(reverse("get_csv_signature", args=[p2.id]))
        self.assertEqual(response.status_code, 403)
        response = self.client.get(reverse("get_csv_confirmed_signature", args=[p2.id]))
        self.assertEqual(response.status_code, 403)
        # Ah right, max does not have access rights for that
        self.login("julia")
        response = self.client.get(reverse("get_csv_signature", args=[p2.id]))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("get_csv_confirmed_signature", args=[p2.id]))
        self.assertEqual(response.status_code, 200)

    def test_show_signatures_post_deleteOK(self):
        julia = self.login("julia")
        petition = julia.petition_set.first()
        pid = petition.id
        signature = Signature.objects.create(
            first_name="Me",
            last_name="You",
            email="you@example.org",
            petition=petition)
        sid = signature.id
        data = {
            'action': 'delete',
            'signature_id': [sid],
        }
        response = self.client.post(reverse("show_signatures", args=[pid]), data, follow=True)
        self.assertRedirects(response, reverse("show_signatures", args=[pid]))
        self.assertTemplateUsed(response, "petition/signature_data.html")
        with self.assertRaises(Signature.DoesNotExist):
            Signature.objects.get(pk=sid)
        messages = response.context['messages']
        self.assertGreaterEqual(len(messages), 1)
        ThereIsAnyError = False
        for msg in messages:
            if msg.level == constants.ERROR:
                ThereIsAnyError = True
        self.assertEqual(ThereIsAnyError, False)

    def test_show_signatures_post_deleteOK_org(self):
        self.login("julia")
        org = Organization.objects.get(name="Les Amis de la Terre")
        petition = org.petition_set.first()
        pid = petition.id
        signature = Signature.objects.create(
            first_name="Me",
            last_name="You",
            email="you@example.org",
            petition=petition)
        sid = signature.id
        data = {
            'action': 'delete',
            'signature_id': [sid],
        }
        response = self.client.post(reverse("show_signatures", args=[pid]), data, follow=True)
        self.assertRedirects(response, reverse("show_signatures", args=[pid]))
        self.assertTemplateUsed(response, "petition/signature_data.html")
        with self.assertRaises(Signature.DoesNotExist):
            Signature.objects.get(pk=sid)
        messages = response.context['messages']
        self.assertGreaterEqual(len(messages), 1)
        ThereIsAnyError = False
        for msg in messages:
            if msg.level == constants.ERROR:
                ThereIsAnyError = True
        self.assertEqual(ThereIsAnyError, False)

    def test_show_signatures_post_deleteKONoRightsUser(self):
        self.login("julia")
        max = PytitionUser.objects.get(user__username="max")
        petition = max.petition_set.first()
        pid = petition.id
        signature = Signature.objects.create(
            first_name="Me",
            last_name="You",
            email="you@example.org",
            petition=petition)
        sid = signature.id
        data = {
            'action': 'delete',
            'signature_id': [sid],
        }
        response = self.client.post(reverse("show_signatures", args=[pid]), data, follow=True)
        self.assertRedirects(response, reverse("user_dashboard"))
        self.assertTemplateUsed(response, "petition/user_dashboard.html")
        s = Signature.objects.get(pk=sid)
        self.assertEqual(s.id, sid) # dummy test, we just want the previous line not to raise a DoesNotExist exception
        messages = response.context['messages']
        self.assertGreaterEqual(len(messages), 1)
        ThereIsAnyError = False
        for msg in messages:
            if msg.level == constants.ERROR:
                ThereIsAnyError = True
        self.assertEqual(ThereIsAnyError, True)

    def test_show_signatures_post_deleteKONoRightsOrg(self):
        self.login("max")
        org = Organization.objects.get(name="Les Amis de la Terre")
        petition = org.petition_set.first()
        pid = petition.id
        signature = Signature.objects.create(
            first_name="Me",
            last_name="You",
            email="you@example.org",
            petition=petition)
        sid = signature.id
        data = {
            'action': 'delete',
            'signature_id': [sid],
        }
        response = self.client.post(reverse("show_signatures", args=[pid]), data, follow=True)
        self.assertRedirects(response, reverse("org_dashboard", args=[org.slugname]))
        self.assertTemplateUsed(response, "petition/org_dashboard.html")
        s = Signature.objects.get(pk=sid)
        self.assertEqual(s.id, sid) # dummy test, we just want the previous line not to raise a DoesNotExist exception
        messages = response.context['messages']
        self.assertGreaterEqual(len(messages), 1)
        ThereIsAnyError = False
        for msg in messages:
            if msg.level == constants.ERROR:
                ThereIsAnyError = True
        self.assertEqual(ThereIsAnyError, True)

    def test_show_signatures_post_resendOK_org(self):
        self.login("julia")
        org = Organization.objects.get(name="Les Amis de la Terre")
        petition = org.petition_set.first()
        pid = petition.id
        signature = Signature.objects.create(
            first_name="Me",
            last_name="You",
            email="you@example.org",
            petition=petition)
        sid = signature.id
        data = {
            'action': 're-send',
            'signature_id': [sid],
        }
        response = self.client.post(reverse("show_signatures", args=[pid]), data, follow=True)
        self.assertRedirects(response, reverse("show_signatures", args=[pid]))
        self.assertTemplateUsed(response, "petition/signature_data.html")
        messages = response.context['messages']
        self.assertGreaterEqual(len(messages), 1)
        ThereIsAnyError = False
        for msg in messages:
            if msg.level == constants.ERROR:
                ThereIsAnyError = True
        self.assertEqual(ThereIsAnyError, False)

    def test_show_signatures_post_resendOK(self):
        julia = self.login("julia")
        petition = julia.petition_set.first()
        pid = petition.id
        signature = Signature.objects.create(
            first_name="Me",
            last_name="You",
            email="you@example.org",
            petition=petition)
        sid = signature.id
        data = {
            'action': 're-send',
            'signature_id': [sid],
        }
        response = self.client.post(reverse("show_signatures", args=[pid]), data, follow=True)
        self.assertRedirects(response, reverse("show_signatures", args=[pid]))
        self.assertTemplateUsed(response, "petition/signature_data.html")
        messages = response.context['messages']
        self.assertGreaterEqual(len(messages), 1)
        ThereIsAnyError = False
        for msg in messages:
            if msg.level == constants.ERROR:
                ThereIsAnyError = True
        self.assertEqual(ThereIsAnyError, False)

    def test_show_signatures_post_resendallOK(self):
        julia = self.login("julia")
        petition = julia.petition_set.first()
        pid = petition.id
        signature = Signature.objects.create(
            first_name="Me",
            last_name="You",
            email="you@example.org",
            petition=petition)
        #sid = signature.id
        data = {
            'action': 're-send-all',
        }
        response = self.client.post(reverse("show_signatures", args=[pid]), data, follow=True)
        self.assertRedirects(response, reverse("show_signatures", args=[pid]))
        self.assertTemplateUsed(response, "petition/signature_data.html")
        messages = response.context['messages']
        self.assertGreaterEqual(len(messages), 1)
        ThereIsAnyError = False
        for msg in messages:
            if msg.level == constants.ERROR:
                ThereIsAnyError = True
        self.assertEqual(ThereIsAnyError, False)

    def test_show_signatures_post_deleteKOCrossPetition(self):
        # A user posting the signature ids of another user's petition on the
        # signatures page of their own petition must not be able to delete them.
        julia = self.login("julia")
        own_petition = julia.petition_set.first()
        max = PytitionUser.objects.get(user__username="max")
        foreign_petition = max.petition_set.first()
        signature = Signature.objects.create(
            first_name="Me",
            last_name="You",
            email="you@example.org",
            petition=foreign_petition)
        sid = signature.id
        data = {
            'action': 'delete',
            'signature_id': [sid],
        }
        response = self.client.post(reverse("show_signatures", args=[own_petition.id]), data, follow=True)
        self.assertRedirects(response, reverse("show_signatures", args=[own_petition.id]))
        self.assertTemplateUsed(response, "petition/signature_data.html")
        # The signature of the other user's petition must still exist
        s = Signature.objects.get(pk=sid)
        self.assertEqual(s.petition, foreign_petition)

    def test_show_signatures_post_resendKOCrossPetition(self):
        # A user posting the signature ids of another user's petition on the
        # signatures page of their own petition must not be able to re-send
        # their confirmation emails.
        julia = self.login("julia")
        own_petition = julia.petition_set.first()
        max = PytitionUser.objects.get(user__username="max")
        foreign_petition = max.petition_set.first()
        signature = Signature.objects.create(
            first_name="Me",
            last_name="You",
            email="you@example.org",
            petition=foreign_petition)
        sid = signature.id
        data = {
            'action': 're-send',
            'signature_id': [sid],
        }
        self.assertEqual(len(mail.outbox), 0)
        response = self.client.post(reverse("show_signatures", args=[own_petition.id]), data, follow=True)
        self.assertRedirects(response, reverse("show_signatures", args=[own_petition.id]))
        self.assertTemplateUsed(response, "petition/signature_data.html")
        # No confirmation email must have been sent to the other user's signer
        self.assertEqual(len(mail.outbox), 0)

    def test_show_signatures_post_resendKONoModifyRightsOrg(self):
        # A member of the organization which does not have the
        # can_modify_signatures right cannot re-send confirmation emails.
        max = self.login("max")
        org = Organization.objects.get(name="Les Amis de la Terre")
        petition = org.petition_set.first()
        pid = petition.id
        perm = Permission.objects.get(organization=org, user=max)
        perm.can_view_signatures = True
        perm.save()
        self.assertTrue(perm.can_view_signatures)
        self.assertFalse(perm.can_modify_signatures)
        signature = Signature.objects.create(
            first_name="Me",
            last_name="You",
            email="you@example.org",
            petition=petition)
        sid = signature.id
        data = {
            'action': 're-send',
            'signature_id': [sid],
        }
        self.assertEqual(len(mail.outbox), 0)
        response = self.client.post(reverse("show_signatures", args=[pid]), data, follow=True)
        self.assertRedirects(response, reverse("show_signatures", args=[pid]))
        self.assertTemplateUsed(response, "petition/signature_data.html")
        messages = response.context['messages']
        ThereIsAnyError = False
        for msg in messages:
            if msg.level == constants.ERROR:
                ThereIsAnyError = True
        self.assertEqual(ThereIsAnyError, True)
        self.assertEqual(len(mail.outbox), 0)

    def test_show_signatures_post_resendallOK_org(self):
        self.login("julia")
        org = Organization.objects.get(name="Les Amis de la Terre")
        petition = org.petition_set.first()
        pid = petition.id
        signature = Signature.objects.create(
            first_name="Me",
            last_name="You",
            email="you@example.org",
            petition=petition)
        #sid = signature.id
        data = {
            'action': 're-send-all',
        }
        response = self.client.post(reverse("show_signatures", args=[pid]), data, follow=True)
        self.assertRedirects(response, reverse("show_signatures", args=[pid]))
        self.assertTemplateUsed(response, "petition/signature_data.html")
        messages = response.context['messages']
        self.assertGreaterEqual(len(messages), 1)
        ThereIsAnyError = False
        for msg in messages:
            if msg.level == constants.ERROR:
                ThereIsAnyError = True
        self.assertEqual(ThereIsAnyError, False)
