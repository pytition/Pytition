from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from petition.models import Organization, Petition, PytitionUser


users = ['julia', 'john']
orgs = ['RAP', 'Greenpeace']

user_petition = {
    'julia': [{
        'title': 'my petition',
        'text': 'bla bla bla',
        'published': True
    }]
}


org_members = {
    'RAP': ['julia'],
    'Greenpeace': [],
}

class PetitionViewTest(TestCase):
    """Test index view"""
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        for org in orgs:
            o = Organization.objects.create(name=org)
            o.save()
        for user in users:
            u = User.objects.create_user(user, password=user)
            u.first_name = user
            u.save()
            pu = PytitionUser.objects.get(user__username=user)
            for petition in user_petition.get(user, []):
                p = Petition.objects.create(user=pu, **petition)

    def tearDown(self):
        # Clean up run after every test method.
        pass

    def login(self, name, password=None):
        self.client.login(username=name, password=password if password else name)
        self.pu = PytitionUser.objects.get(user__username=name)
        return self.pu

    def logout(self):
        self.client.logout()

    def test_petition_detail(self):
        """ every body should see the petition, even when not logged in """
        petition = Petition.objects.get(title="my petition")
        response = self.client.get(reverse("detail", args=[petition.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['petition'], petition)
        self.assertTemplateUsed(response, "petition/petition_detail.html")

        self.assertContains(response, text='<meta property="og:site_name" content="testserver" />')
        self.assertContains(response, text='<meta property="og:url" content="http://testserver/petition/{}/" />'.format(petition.id))

    def test_petition_publish(self):
        self.logout()
        petition = Petition.objects.get(title="my petition")
        petition.published = False
        petition.save()
        self.assertEqual(petition.published, False)
        response = self.client.get(reverse("petition_publish", args=[petition.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(petition.published, False)
        julia = self.login('julia')
        # Logged in with same user
        response = self.client.get(reverse("petition_publish", args=[petition.id]))
        self.assertEqual(response.status_code, 200)
        petition.refresh_from_db()
        self.assertEqual(petition.published, True)
        # Petition for another user
        john = PytitionUser.objects.get(user__username='john')
        p2 = Petition.objects.create(title='Pas content', user=john)
        self.assertEqual(p2.published, False)
        response = self.client.get(reverse("petition_publish", args=[p2.id]))
        p2.refresh_from_db()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(p2.published, False)
        # Petition from another organisation
        greenpeace = Organization.objects.get(name='Greenpeace')
        p3 = Petition.objects.create(title='Sauver la planete', org=greenpeace)
        self.assertEqual(p3.published, False)
        p3.refresh_from_db()
        response = self.client.get(reverse("petition_publish", args=[p3.id]))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(p3.published, False)

    def test_petition_unpublish(self):
        petition = Petition.objects.get(title="my petition")
        self.assertEqual(petition.published, True)
        self.logout()
        response = self.client.get(reverse("petition_unpublish", args=[petition.id]))
        petition.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(petition.published, True)
        self.login('julia')
        response = self.client.get(reverse("petition_unpublish", args=[petition.id]))
        petition.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(petition.published, False)

    def test_petition_delete(self):
        petition = Petition.objects.get(title="my petition")
        self.assertEqual(Petition.objects.count(),  1)
        response = self.client.get(reverse("petition_delete", args=[petition.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Petition.objects.count(),  1)
        self.login('julia')
        response = self.client.get(reverse("petition_delete", args=[petition.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Petition.objects.count(),  0)

    def test_user_slug_show_petition(self):
        petition = Petition.objects.get(title="my petition")
        slug = petition.slugmodel_set.first().slug
        response = self.client.get(reverse("slug_show_petition", args=[petition.user.username, slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "petition/petition_detail.html")

    def pending_org_slug_show_petition(self):
        # Problem here
        org = Organization.objects.first()
        petition = Petition.objects.create(title="NON NON NON", org=org)
        slug = petition.slugmodel_set.first().slug
        response = self.client.get(reverse("slug_show_petition", args=[petition.org.slugname, slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "petition/petition_detail.html")
