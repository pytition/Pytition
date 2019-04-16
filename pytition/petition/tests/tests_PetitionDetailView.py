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

class PetitionDetailViewTest(TestCase):
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
                p = Petition.objects.create(**petition)
                p.id
                pu.petitions.add(p)
                p.save()

    def login(self, name):
        self.client.login(username=name, password=name)
        self.pu = PytitionUser.objects.get(user__username=name)

    def logout(self):
        self.client.logout()

    def tearDown(self):
        # Clean up run after every test method.
        pass

    def test_petition_detail(self):
        """ every body should see the petition, even when not logged in """
        petition = Petition.objects.get(title="my petition")
        response = self.client.get(reverse("detail", args=[petition.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['petition'], petition)
        self.assertTemplateUsed(response, "petition/petition_detail.html")

        self.assertContains(response, text='<meta property="og:site_name" content="testserver" />')
        self.assertContains(response, text='<meta property="og:url" content="http://testserver/petition/1/" />')
