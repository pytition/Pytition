from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import constants

from petition.models import Organization, Petition, PytitionUser, Signature, Permission
from .utils import add_default_data


class PetitionViewTest(TestCase):
    """Test index view"""
    @classmethod
    def setUpTestData(cls):
        """
        Sets the default data set.

        Args:
            cls: (todo): write your description
        """
        add_default_data()

    def tearDown(self):
        """
        Tear down the next callable.

        Args:
            self: (todo): write your description
        """
        # Clean up run after every test method.
        pass

    def login(self, name, password=None):
        """
        Login with the given credentials.

        Args:
            self: (todo): write your description
            name: (str): write your description
            password: (str): write your description
        """
        self.client.login(username=name, password=password if password else name)
        self.pu = PytitionUser.objects.get(user__username=name)
        return self.pu

    def logout(self):
        """
        Logout of the client.

        Args:
            self: (todo): write your description
        """
        self.client.logout()

    def test_show_signatures(self):
        """
        Show the details of the organization.

        Args:
            self: (todo): write your description
        """
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
        """
        Fet of the signature.

        Args:
            self: (todo): write your description
        """
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
        """
        Show the details : return :

        Args:
            self: (todo): write your description
        """
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
        self.assertEquals(ThereIsAnyError, False)

    def test_show_signatures_post_deleteOK_org(self):
        """
        Show the organization organization for the organization.

        Args:
            self: (todo): write your description
        """
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
        self.assertEquals(ThereIsAnyError, False)

    def test_show_signatures_post_deleteKONoRightsUser(self):
        """
        Test if the user s signatures.

        Args:
            self: (todo): write your description
        """
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
        self.assertEquals(s.id, sid) # dummy test, we just want the previous line not to raise a DoesNotExist exception
        messages = response.context['messages']
        self.assertGreaterEqual(len(messages), 1)
        ThereIsAnyError = False
        for msg in messages:
            if msg.level == constants.ERROR:
                ThereIsAnyError = True
        self.assertEquals(ThereIsAnyError, True)

    def test_show_signatures_post_deleteKONoRightsOrg(self):
        """
        : return the organization.

        Args:
            self: (todo): write your description
        """
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
        self.assertEquals(s.id, sid) # dummy test, we just want the previous line not to raise a DoesNotExist exception
        messages = response.context['messages']
        self.assertGreaterEqual(len(messages), 1)
        ThereIsAnyError = False
        for msg in messages:
            if msg.level == constants.ERROR:
                ThereIsAnyError = True
        self.assertEquals(ThereIsAnyError, True)

    def test_show_signatures_post_resendOK_org(self):
        """
        : param organization : :

        Args:
            self: (todo): write your description
        """
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
        self.assertEquals(ThereIsAnyError, False)

    def test_show_signatures_post_resendOK(self):
        """
        : return : return :

        Args:
            self: (todo): write your description
        """
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
        self.assertEquals(ThereIsAnyError, False)

    def test_show_signatures_post_resendallOK(self):
        """
        Show the signatures of the user.

        Args:
            self: (todo): write your description
        """
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
        self.assertEquals(ThereIsAnyError, False)

    def test_show_signatures_post_resendallOK_org(self):
        """
        : param organization : : return :

        Args:
            self: (todo): write your description
        """
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
        self.assertEquals(ThereIsAnyError, False)
