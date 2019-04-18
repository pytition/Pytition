from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.text import slugify

from petition.models import Organization, Petition, PytitionUser


users = ['julia', 'john', 'max', 'sarah']
orgs = ['RAP', 'Greenpeace', 'Attac', 'Les Amis de la Terre']

user_published_petitions = {
    'john': 0,
    'sarah': 0,
    'julia': 5,
    'max': 10
}

user_unpublished_petitions = {
    'john': 0,
    'sarah': 5,
    'julia': 0,
    'max': 10
}

org_published_petitions = {
    'RAP': 0,
    'Les Amis de la Terre': 0,
    'Greenpeace': 1,
    'Attac': 2
}

org_unpublished_petitions = {
    'RAP': 0,
    'Les Amis de la Terre': 1,
    'Greenpeace': 0,
    'Attac': 2
}

org_members = {
    'RAP': ['julia'],
    'Les Amis de la Terre': ['julia', 'max'],
    'Attac': ['john'],
}

class AddSlugViewTest(TestCase):
    """Test Slug creation view"""
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        for org in orgs:
            o = Organization.objects.create(name=org)
            for i in range(org_published_petitions[org]):
                p = Petition.objects.create(published=True)
                o.petitions.add(p)
                p.save()
            for i in range(org_unpublished_petitions[org]):
                p = Petition.objects.create(published=False)
                o.petitions.add(p)
                p.save()
            o.save()
        for user in users:
            u = User.objects.create_user(user, password=user)
            u.first_name = user
            u.last_name = user + "Last"
            u.save()
            pu = PytitionUser.objects.get(user__username=user)
            for i in range(user_published_petitions[user]):
                p = Petition.objects.create(published=True)
                pu.petitions.add(p)
                p.save()
            for i in range(user_unpublished_petitions[user]):
                p = Petition.objects.create(published=False)
                pu.petitions.add(p)
                p.save()
        for orgname in org_members:
            org = Organization.objects.get(name=orgname)
            for username in org_members[orgname]:
                user = PytitionUser.objects.get(user__username=username)
                org.add_member(user)

        # give julia can_modify_petitions permission on "Les Amis de la Terre" organization
        perm = PytitionUser.objects.get(user__username="julia").permissions\
            .get(organization__name="Les Amis de la Terre")
        perm.can_modify_petitions = True
        perm.save()

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
        petition = max.petitions.all()[0]
        slugtext = 'coucou ceci est un slug'
        data = {
            'slugtext': slugtext,
        }
        previous_slug_count = petition.slugs.count()
        response = self.client.post(reverse("add_new_slug", args=[petition.id]), data, follow=True)
        self.assertRedirects(response, reverse("edit_petition", args=[petition.id]) + "#tab_social_network_form")
        slug_count = petition.slugs.count()
        self.assertEqual(slug_count, previous_slug_count + 1)
        new_slug = petition.slugs.get(slug=slugify(slugtext))
        self.assertEqual(new_slug.slug, slugify(slugtext))

    def test_addSlugAlreadyExistsKO(self):
        max = self.login("max")
        petition = max.petitions.all()[0]
        slugtext = 'coucou ceci est un slug'
        data = {
            'slugtext': slugtext,
        }
        previous_slug_count = petition.slugs.count()
        # first time slug insertion
        response = self.client.post(reverse("add_new_slug", args=[petition.id]), data, follow=True)
        self.assertRedirects(response, reverse("edit_petition", args=[petition.id]) + "#tab_social_network_form")
        slug_count = petition.slugs.count()
        self.assertEqual(slug_count, previous_slug_count + 1)
        new_slug = petition.slugs.get(slug=slugify(slugtext))
        self.assertEqual(new_slug.slug, slugify(slugtext))
        # second time slug insertion (should fail)
        response = self.client.post(reverse("add_new_slug", args=[petition.id]), data, follow=True)
        self.assertRedirects(response, reverse("edit_petition", args=[petition.id]) + "#tab_social_network_form")
        slug_count = petition.slugs.count()
        self.assertEqual(slug_count, previous_slug_count + 1)
        new_slug = petition.slugs.get(slug=slugify(slugtext))
        self.assertEqual(new_slug.slug, slugify(slugtext))
