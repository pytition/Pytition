from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from petition.models import Organization, Petition, PytitionUser, Permission
from .utils import add_default_data


class EditPetitionViewTest(TestCase):
    """Test index view"""
    @classmethod
    def setUpTestData(cls):
        add_default_data()

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
        petition = self.pu.petition_set.first()
        response = self.client.get(reverse("edit_petition", args=[petition.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['petition'], petition)
        self.assertTemplateUsed(response, "petition/edit_petition.html")

    def test_edit_loggedout(self):
        """ edit your own petition while being logged out """
        self.login('julia')
        petition = self.pu.petition_set.first()
        self.logout()
        response = self.client.get(reverse("edit_petition", args=[petition.id]), follow=True)
        self.assertRedirects(response, reverse("login")+"?next="+reverse("edit_petition", args=[petition.id]))

    def test_edit_notYourOwnPetition(self):
        """ editing somebody else's petition """
        self.login('julia')
        max = PytitionUser.objects.get(user__username="max")
        petition = max.petition_set.first()
        response = self.client.get(reverse("edit_petition", args=[petition.id]), follow=True)
        self.assertRedirects(response, reverse("user_dashboard"))
        self.assertTemplateUsed(response, "petition/user_dashboard.html")

    def test_edit_notInOrg(self):
        """ editing a petition owned by an Organization the logged-in user is *NOT* part of """
        self.login('sarah')
        attac = Organization.objects.get(name='Les Amis de la Terre')
        petition = attac.petition_set.first()
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
        max = PytitionUser.objects.get(user__username="max")
        perm = Permission.objects.get(organization=at, user=max)
        perm.can_modify_petitions = False
        perm.save()
        petition = at.petition_set.first()
        response = self.client.get(reverse("edit_petition", args=[petition.id]), follow=True)
        self.assertRedirects(response, reverse("user_dashboard"))

    def test_edit_InOrgWithEditPerm(self):
        """
        editing a petition owned by an Organization the logged-in user is part of
        *AND* with the can_modify_petitions permission
        """
        self.login('julia')
        at = Organization.objects.get(name='Les Amis de la Terre')
        petition = at.petition_set.first()
        response = self.client.get(reverse("edit_petition", args=[petition.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['petition'], petition)
        self.assertTemplateUsed(response, "petition/edit_petition.html")
