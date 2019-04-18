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

org_members = {
    'RAP': ['julia'],
    'Les Amis de la Terre': ['julia', 'max'],
    'Attac': ['john'],
}

class UserDashboardViewTest(TestCase):
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
            u = User.objects.create_user(user, password=user)
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

    def login(self, name):
        self.client.login(username=name, password=name)
        self.pu = PytitionUser.objects.get(user__username=name)
        return self.pu

    def logout(self):
        self.client.logout()

    def tearDown(self):
        # Clean up run after every test method.
        pass

    def test_NotLoggedIn(self):
        self.logout()
        response = self.client.get(reverse("user_dashboard"), follow=True)
        self.assertRedirects(response, reverse("login")+"?next="+reverse("user_dashboard"))
        self.assertTemplateUsed(response, "registration/login.html")
        self.assertTemplateUsed(response, "petition/base.html")

    def test_UserOK1(self):
        john = self.login("john")
        num_petitions = john.petitions.count()

        response = self.client.get(reverse("user_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "petition/user_dashboard.html")
        self.assertTemplateUsed(response, "petition/user_base.html")
        self.assertTemplateUsed(response, "petition/base.html")
        petitions = response.context['petitions'].all()
        self.assertEqual(len(petitions), num_petitions)
        self.assertEqual(response.context['user'], john)

    def test_UserOK2(self):
        julia = self.login("julia")
        num_petitions = julia.petitions.count()

        response = self.client.get(reverse("user_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "petition/user_dashboard.html")
        self.assertTemplateUsed(response, "petition/user_base.html")
        self.assertTemplateUsed(response, "petition/base.html")
        petitions = response.context['petitions'].all()
        self.assertEqual(len(petitions), num_petitions)
        self.assertEqual(response.context['user'], julia)

    def test_UserOK3(self):
        max = self.login("max")
        num_petitions = max.petitions.count()

        response = self.client.get(reverse("user_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "petition/user_dashboard.html")
        self.assertTemplateUsed(response, "petition/user_base.html")
        self.assertTemplateUsed(response, "petition/base.html")
        petitions = response.context['petitions'].all()
        self.assertEqual(len(petitions), num_petitions)
        self.assertEqual(response.context['user'], max)

    def test_UserOK4(self):
        sarah = self.login("sarah")
        num_petitions = sarah.petitions.count()

        response = self.client.get(reverse("user_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "petition/user_dashboard.html")
        self.assertTemplateUsed(response, "petition/user_base.html")
        self.assertTemplateUsed(response, "petition/base.html")
        petitions = response.context['petitions'].all()
        self.assertEqual(len(petitions), num_petitions)
        self.assertEqual(response.context['user'], sarah)