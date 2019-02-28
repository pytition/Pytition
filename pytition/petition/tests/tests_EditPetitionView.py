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

class EditPetitionViewTest(TestCase):
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

    def logout(self):
        self.client.logout()

    def tearDown(self):
        # Clean up run after every test method.
        pass

    def test_edit_404(self):
        """ Non-existent petition id : should return 404 """
        self.login("julia")
        response = self.client.get(reverse("edit_petition", args=[1000]))
        self.assertEqual(response.status_code, 404)

    def test_edit_200(self):
        """ edit your own petition while being logged-in """
        self.login('julia')
        petition = self.pu.petitions.first()
        response = self.client.get(reverse("edit_petition", args=[petition.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['petition'], petition)
        self.assertTemplateUsed(response, "petition/edit_petition.html")

    def test_edit_loggedout(self):
        """ edit your own petition while being logged out """
        self.login('julia')
        petition = self.pu.petitions.first()
        self.logout()
        response = self.client.get(reverse("edit_petition", args=[petition.id]), follow=True)
        self.assertRedirects(response, reverse("login")+"?next="+reverse("edit_petition", args=[petition.id]))

    def test_edit_notYourOwnPetition(self):
        """ editing somebody else's petition """
        self.login('julia')
        max = PytitionUser.objects.get(user__username="max")
        petition = max.petitions.first()
        response = self.client.get(reverse("edit_petition", args=[petition.id]), follow=True)
        self.assertRedirects(response, reverse("user_dashboard"))
        self.assertTemplateUsed(response, "petition/user_dashboard.html")

    def test_edit_notInOrg(self):
        """ editing a petition owned by an Organization the logged-in user is *NOT* part of """
        self.login('sarah')
        attac = Organization.objects.get(name='Les Amis de la Terre')
        petition = attac.petitions.first()
        response = self.client.get(reverse("edit_petition", args=[petition.id]), follow=True)
        self.assertRedirects(response, reverse("user_dashboard"))
        self.assertTemplateUsed(response, "petition/user_dashboard.html")

    def test_edit_InOrgButNoEditPermission(self):
        """
        editing a petition owned by an Organization the logged-in user is part of
        but without the can_modify_petitions permission
        """
        self.login('max')
        at = Organization.objects.get(name='Les Amis de la Terre')
        petition = at.petitions.first()
        response = self.client.get(reverse("edit_petition", args=[petition.id]), follow=True)
        self.assertRedirects(response, reverse("org_dashboard", args=[at.name]))
        self.assertTemplateUsed(response, "petition/org_dashboard.html")

    def test_edit_InOrgWithEditPerm(self):
        """
        editing a petition owned by an Organization the logged-in user is part of
        *AND* with the can_modify_petitions permission
        """
        self.login('julia')
        at = Organization.objects.get(name='Les Amis de la Terre')
        petition = at.petitions.first()
        response = self.client.get(reverse("edit_petition", args=[petition.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['petition'], petition)
        self.assertTemplateUsed(response, "petition/edit_petition.html")