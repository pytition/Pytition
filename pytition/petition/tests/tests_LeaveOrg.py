from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from petition.models import Organization, Petition, PytitionUser, Permission


users = ['julia', 'john', 'max', 'sarah']
orgs = ['RAP', 'Greenpeace', 'Attac', 'Les Amis de la Terre']

org_members = {
    'RAP': ['julia'],
    'Les Amis de la Terre': ['julia', 'max'],
    'Attac': ['john'],
}

class LeaveOrgViewTest(TestCase):
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
            u.last_name = user + "Last"
            u.save()
            pu = PytitionUser.objects.get(user__username=user)
        for orgname in org_members:
            org = Organization.objects.get(name=orgname)
            for username in org_members[orgname]:
                user = PytitionUser.objects.get(user__username=username)
                user.organizations.add(org)
                permission = Permission.objects.create(organization=org, can_modify_permissions=True)
                permission.save()
                user.permissions.add(permission)
                user.save()

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

    def test_NotLoggedIn(self):
        self.logout()
        org = Organization.objects.get(name='RAP')
        response = self.client.get(reverse("leave_org", args=[org.slugname]), follow=True)
        self.assertRedirects(response, reverse("login")+"?next="+reverse("leave_org", args=[org.slugname]))
        self.assertTemplateUsed(response, "registration/login.html")
        self.assertTemplateUsed(response, "petition/base.html")

    def test_leave_org_ok(self):
        julia = self.login("julia")
        org = Organization.objects.get(name='Les Amis de la Terre')
        response = self.client.get(reverse("leave_org", args=[org.slugname]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("account_settings"))
        self.assertNotIn(org, julia.organizations.all())

    def test_leave_refuse_alone(self):
        julia = self.login("julia")
        org = Organization.objects.get(name='RAP')
        response = self.client.get(reverse("leave_org", args=[org.slugname]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("account_settings") + '#a_org_form')
        self.assertIn(org, julia.organizations.all())

