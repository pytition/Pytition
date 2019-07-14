from django.test import TestCase
from django.urls import reverse

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
