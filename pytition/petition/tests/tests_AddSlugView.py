from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.text import slugify

from petition.models import Organization, Petition, PytitionUser
from .utils import add_default_data


class AddSlugViewTest(TestCase):
    """Test Slug creation view"""
    @classmethod
    def setUpTestData(cls):
        add_default_data()

    def login(self, name, password=None):
        self.client.login(username=name, password=password if password else name)
        self.pu = PytitionUser.objects.get(user__username=name)
        return self.pu

    def logout(self):
        self.client.logout()

    def tearDown(self):
        # Clean up run after every test method.
        pass

    def test_addSlugOK(self):
        max = self.login("max")
        petition = max.petition_set.all()[0]
        slugtext = 'coucou ceci est un slug'
        data = {
            'slugtext': slugtext,
        }
        previous_slug_count = petition.slugmodel_set.count()
        response = self.client.post(reverse("add_new_slug", args=[petition.id]), data, follow=True)
        self.assertRedirects(response, reverse("edit_petition", args=[petition.id]) + "#tab_social_network_form")
        slug_count = petition.slugmodel_set.count()
        self.assertEqual(slug_count, previous_slug_count + 1)
        new_slug = petition.slugmodel_set.get(slug=slugify(slugtext))
        self.assertEqual(new_slug.slug, slugify(slugtext))

    def test_addSlugAlreadyExistsKO(self):
        max = self.login("max")
        petition = max.petition_set.all()[0]
        slugtext = 'coucou ceci est un slug'
        data = {
            'slugtext': slugtext,
        }
        previous_slug_count = petition.slugmodel_set.count()
        # first time slug insertion
        response = self.client.post(reverse("add_new_slug", args=[petition.id]), data, follow=True)
        self.assertRedirects(response, reverse("edit_petition", args=[petition.id]) + "#tab_social_network_form")
        slug_count = petition.slugmodel_set.count()
        self.assertEqual(slug_count, previous_slug_count + 1)
        new_slug = petition.slugmodel_set.get(slug=slugify(slugtext))
        self.assertEqual(new_slug.slug, slugify(slugtext))
        # second time slug insertion (should fail)
        with self.assertRaises(ValueError):
            response = self.client.post(reverse("add_new_slug", args=[petition.id]), data, follow=True)
            self.assertRedirects(response, reverse("edit_petition", args=[petition.id]) + "#tab_social_network_form")
        slug_count = petition.slugmodel_set.count()
        self.assertEqual(slug_count, previous_slug_count + 1)
        new_slug = petition.slugmodel_set.get(slug=slugify(slugtext))
        self.assertEqual(new_slug.slug, slugify(slugtext))
