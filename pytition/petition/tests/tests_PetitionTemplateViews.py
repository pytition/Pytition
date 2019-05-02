from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from petition.models import Organization, Petition, PytitionUser, PetitionTemplate
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

    def test_org_new_template_get(self):
        # GET request just shows the page
        # Not logged
        org = Organization.objects.get(name='RAP')
        response = self.client.get(reverse("org_new_template", args=[org.slugname]))
        self.assertEqual(response.status_code, 302)
        # Logged
        self.login('julia')
        response = self.client.get(reverse("org_new_template", args=[org.slugname]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "petition/new_template.html")

    def test_org_new_template_post(self):
        self.login('julia')
        org = Organization.objects.get(name='RAP')
        self.assertEqual(org.petitiontemplate_set.count(), 0)
        data = {'template_name': 'This is a default template'}
        response = self.client.post(reverse("org_new_template", args=[org.slugname]), data)
        self.assertEqual(org.petitiontemplate_set.count(), 1)
        self.assertEqual(response.status_code, 302)
        pt = org.petitiontemplate_set.first()
        self.assertRedirects(response, reverse("edit_template", args=[pt.id]))

    def test_edit_template(self):
        self.login('julia')
        org = Organization.objects.get(name='RAP')
        julia = PytitionUser.objects.get(user__username='julia')
        # For an org template
        pt = PetitionTemplate.objects.create(name="Default template", org=org)
        response = self.client.get(reverse("edit_template", args=[pt.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "petition/edit_template.html")
        # For an user template
        pt2 = PetitionTemplate.objects.create(name="Default template", user=julia)
        response = self.client.get(reverse("edit_template", args=[pt2.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "petition/edit_template.html")
