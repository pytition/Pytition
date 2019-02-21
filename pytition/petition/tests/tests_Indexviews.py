from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

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

class IndexViewTest(TestCase):
    """Test index view"""
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
            u = User.objects.create_user(user)
            u.first_name = user
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


    def tearDown(self):
        # Clean up run after every test method.
        pass

    def test_index_all_petition(self):
        total_published_petitions = sum(org_published_petitions.values()) + sum(user_published_petitions.values())
        with self.settings(INDEX_PAGE="ALL_PETITIONS"):
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.context['petitions']), total_published_petitions)

    def test_index_orga_petitions(self):
        for org in orgs:
            with self.settings(INDEX_PAGE="ORGA_PETITIONS", INDEX_PAGE_ORGA=org):
                response = self.client.get('/')
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response.context['petitions']), org_published_petitions[org])

    def test_index_user_petitions(self):
        for user in users:
            with self.settings(INDEX_PAGE="USER_PETITIONS", INDEX_PAGE_USER=user):
                response = self.client.get('/')
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response.context['petitions']), user_published_petitions[user])

    def test_index_orga_profile(self):
        for org in orgs:
            with self.settings(INDEX_PAGE="ORGA_PROFILE", INDEX_PAGE_ORGA=org):
                response = self.client.get('/', follow=True)
                self.assertRedirects(response, reverse("org_profile", args=[org]))
                self.assertEqual(len(response.context['petitions']), org_published_petitions[org])

    def test_index_user_profile(self):
        for user in users:
            with self.settings(INDEX_PAGE="USER_PROFILE", INDEX_PAGE_USER=user):
                response = self.client.get('/', follow=True)
                self.assertRedirects(response, reverse("user_profile", args=[user]))
                self.assertEqual(len(response.context['petitions']), user_published_petitions[user])

    def test_index_login_register(self):
        with self.settings(INDEX_PAGE="LOGIN_REGISTER"):
            response = self.client.get('/', follow=True)
            self.assertRedirects(response, reverse("login"))

            User = get_user_model()
            user = User.objects.create_user('temporary', 'temporary@temporary.com', 'temporary')
            pu = PytitionUser.objects.get(user__username=user)
            self.client.login(username='temporary', password='temporary')

            response = self.client.get('/', follow=True)
            self.assertRedirects(response, reverse("user_dashboard"))
            self.assertEquals(response.context['user'], pu)