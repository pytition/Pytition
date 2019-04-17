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

class OrgCreateViewTest(TestCase):
    """Test Org Creation view"""
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

    def test_CreateOK(self):
        john = self.login("john")
        newname = 'my new-org with @ ç special_chars'
        previous_org_numbers = len(john.organizations.all())
        data = {
            'name': newname,
        }
        response = self.client.post(reverse("org_create"), data, follow=True)
        self.assertRedirects(response, reverse("user_dashboard"))
        user = response.context['user']
        orgs = user.organizations.all()
        self.assertEquals(user, john)
        self.assertEquals(len(orgs), previous_org_numbers + 1)
        org = Organization.objects.get(slugname=slugify(newname))
        self.assertEqual(org.slugname, slugify(newname))
        self.assertEqual(org.name, newname)

    def test_CreateAlreadyExistsKO(self):
        john = self.login("john")
        newname = 'my new-org with @ ç special_chars'
        previous_org_numbers = len(john.organizations.all())
        data = {
            'name': newname,
        }
        # first creation
        response = self.client.post(reverse("org_create"), data, follow=True)
        self.assertRedirects(response, reverse("user_dashboard"))
        user = response.context['user']
        orgs = user.organizations.all()
        self.assertEquals(user, john)
        self.assertEquals(len(orgs), previous_org_numbers + 1)
        org = Organization.objects.get(slugname=slugify(newname))
        self.assertEqual(org.slugname, slugify(newname))
        self.assertEqual(org.name, newname)

        # second creation try
        response = self.client.post(reverse("org_create"), data, follow=True)
        self.assertEquals(response.status_code, 200)
        org_count = user.organizations.filter(name=newname).count()
        self.assertEquals(org_count, 1)

    def test_CreateEmptyKO(self):
        john = self.login("john")
        newname = ''
        previous_org_numbers = len(john.organizations.all())
        data = {
            'name': newname,
        }
        response = self.client.post(reverse("org_create"), data)
        self.assertEquals(response.status_code, 200)
        user = response.context['user']
        orgs = user.organizations.all()
        self.assertEquals(user, john)
        self.assertEquals(len(orgs), previous_org_numbers)
        empty_org_name_number = Organization.objects.filter(name='').count()
        self.assertEqual(empty_org_name_number, 0)

    def test_UserUnauthenticatedKO(self):
        self.logout()
        newname = 'my new-org with @ ç special_chars'
        data = {
            'name': newname,
        }
        previous_org_num = Organization.objects.count()
        response = self.client.post(reverse("org_create"), data, follow=True)
        self.assertRedirects(response, reverse("login")+"?next="+reverse("org_create"))
        new_org_num = Organization.objects.count()
        self.assertEqual(previous_org_num, new_org_num)