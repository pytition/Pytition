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

class PetitionCreateWizardViewTest(TestCase):
    """Test PetitionCreateWizard view"""
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
        for orgname in org_members:
            org = Organization.objects.get(name=orgname)
            for username in org_members[orgname]:
                user = PytitionUser.objects.get(user__username=username)
                org.members.add(user)
                permission = Permission.objects.get(organization=org, user=user)
                permission.can_modify_permissions=True
                permission.save()

        # give julia can_modify_petitions permission on "Les Amis de la Terre" organization
        user = PytitionUser.objects.get(user__username='julia')
        org = Organization.objects.get(name="Les Amis de la Terre")
        perm = Permission.objects.get(organization=org, user=user)
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
        response = self.client.get(reverse("org_petition_wizard", args=[org.slugname]), follow=True)
        self.assertRedirects(response, reverse("login")+"?next="+reverse("org_petition_wizard", args=[org.slugname]))
        self.assertTemplateUsed(response, "registration/login.html")
        self.assertTemplateUsed(response, "layouts/base.html")

    def test_call_page1_ok(self):
        self.login("julia")
        org = Organization.objects.get(name='Les Amis de la Terre')
        response = self.client.get(reverse("org_petition_wizard", args=[org.slugname]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "petition/org_base.html")

    def test_call_page2_ok(self):
        self.login("julia")
        org = Organization.objects.get(name='Les Amis de la Terre')
        response = self.client.get(reverse("user_petition_wizard"))
        self.assertEqual(response.status_code, 200)
