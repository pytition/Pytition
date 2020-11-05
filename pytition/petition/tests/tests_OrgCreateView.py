from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.text import slugify

from petition.models import Organization, Petition, PytitionUser, Permission
from .utils import add_default_data


class OrgCreateViewTest(TestCase):
    """Test Org Creation view"""
    @classmethod
    def setUpTestData(cls):
        """
        Sets the default data set.

        Args:
            cls: (todo): write your description
        """
        add_default_data()

    def login(self, name, password=None):
        """
        Login with the given credentials.

        Args:
            self: (todo): write your description
            name: (str): write your description
            password: (str): write your description
        """
        self.client.login(username=name, password=password if password else name)
        self.pu = PytitionUser.objects.get(user__username=name)
        return self.pu

    def logout(self):
        """
        Logout of the client.

        Args:
            self: (todo): write your description
        """
        self.client.logout()

    def tearDown(self):
        """
        Tear down the next callable.

        Args:
            self: (todo): write your description
        """
        # Clean up run after every test method.
        pass

    def test_CreateGetFormOK(self):
        """
        Gets the login request.

        Args:
            self: (todo): write your description
        """
        john = self.login("john")
        response = self.client.get(reverse("org_create"))
        self.assertEquals(response.status_code, 200)

    def test_CreateOK(self):
        """
        Creates a new organization.

        Args:
            self: (todo): write your description
        """
        john = self.login("john")
        newname = 'my new-org with @ ç special_chars'
        previous_org_numbers = john.organization_set.count()
        data = {
            'name': newname,
        }
        response = self.client.post(reverse("org_create"), data, follow=True)
        self.assertRedirects(response, reverse("user_dashboard"))
        user = response.context['user']
        orgs = user.organization_set.all()
        self.assertEquals(user, john)
        self.assertEquals(len(orgs), previous_org_numbers + 1)
        org = Organization.objects.get(slugname=slugify(newname))
        self.assertEqual(org.slugname, slugify(newname))
        self.assertEqual(org.name, newname)
        admins_perms = Permission.objects.filter(organization=org, can_modify_permissions=True)
        self.assertGreaterEqual(admins_perms.count(), 1)

    def test_CreateAlreadyExistsKO(self):
        """
        Creates a new organization.

        Args:
            self: (todo): write your description
        """
        john = self.login("john")
        newname = 'my new-org with @ ç special_chars'
        previous_org_numbers = john.organization_set.count()
        data = {
            'name': newname,
        }
        # first creation
        response = self.client.post(reverse("org_create"), data, follow=True)
        self.assertRedirects(response, reverse("user_dashboard"))
        user = response.context['user']
        orgs = user.organization_set.all()
        self.assertEquals(user, john)
        self.assertEquals(len(orgs), previous_org_numbers + 1)
        org = Organization.objects.get(slugname=slugify(newname))
        self.assertEqual(org.slugname, slugify(newname))
        self.assertEqual(org.name, newname)

        # second creation try
        response = self.client.post(reverse("org_create"), data, follow=True)
        self.assertEquals(response.status_code, 200)
        org_count = user.organization_set.filter(name=newname).count()
        self.assertEquals(org_count, 1)

    def test_CreateEmptyKO(self):
        """
        Creates an organization.

        Args:
            self: (todo): write your description
        """
        john = self.login("john")
        newname = ''
        previous_org_numbers = john.organization_set.count()
        data = {
            'name': newname,
        }
        response = self.client.post(reverse("org_create"), data)
        self.assertEquals(response.status_code, 200)
        user = response.context['user']
        orgs = user.organization_set.all()
        self.assertEquals(user, john)
        self.assertEquals(len(orgs), previous_org_numbers)
        empty_org_name_number = Organization.objects.filter(name='').count()
        self.assertEqual(empty_org_name_number, 0)

    def test_UserUnauthenticatedKO(self):
        """
        Test if the user is authenticated.

        Args:
            self: (todo): write your description
        """
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

    @override_settings(RESTRICT_ORG_CREATION=True)
    def test_restrict_org_creation(self):
        """
        Initialize the organization to the organization.

        Args:
            self: (todo): write your description
        """
        init_org_number = Organization.objects.count()
        self.login("john")

        response = self.client.get(reverse("org_create"), follow=True)
        self.assertRedirects(response, reverse("user_dashboard"))
        self.assertContains(response, "Only super users can create an organization.")

        data = {'name': 'New Org'}
        response = self.client.post(reverse("org_create"), data, follow=True)
        self.assertRedirects(response, reverse("user_dashboard"))
        self.assertEquals(Organization.objects.count(), init_org_number)
        self.assertContains(response, "Only super users can create an organization.")

        self.login("admin")
        response = self.client.post(reverse("org_create"), data, follow=True)
        self.assertRedirects(response, reverse("user_dashboard"))
        self.assertEquals(Organization.objects.count(), init_org_number + 1)
        self.assertNotContains(response, "Only super users can create an organization.")
