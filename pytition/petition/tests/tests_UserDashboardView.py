from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from petition.models import Organization, Petition, PytitionUser, Permission
from .utils import add_default_data


class UserDashboardViewTest(TestCase):
    """Test index view"""
    @classmethod
    def setUpTestData(cls):
        """
        Sets the default data set.

        Args:
            cls: (todo): write your description
        """
        add_default_data()

    def login(self, name):
        """
        Authenticate with the server.

        Args:
            self: (todo): write your description
            name: (str): write your description
        """
        self.client.login(username=name, password=name)
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

    def test_NotLoggedIn(self):
        """
        Respond to be logged in.

        Args:
            self: (todo): write your description
        """
        self.logout()
        response = self.client.get(reverse("user_dashboard"), follow=True)
        self.assertRedirects(response, reverse("login")+"?next="+reverse("user_dashboard"))
        self.assertTemplateUsed(response, "registration/login.html")
        self.assertTemplateUsed(response, "layouts/base.html")

    def test_UserOK1(self):
        """
        Test if user authentication.

        Args:
            self: (todo): write your description
        """
        john = self.login("john")
        num_petitions = john.petition_set.count()

        response = self.client.get(reverse("user_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "petition/user_dashboard.html")
        self.assertTemplateUsed(response, "petition/user_base.html")
        self.assertTemplateUsed(response, "layouts/base.html")
        petitions = response.context['petitions'].all()
        self.assertEqual(len(petitions), num_petitions)
        self.assertEqual(response.context['user'], john)

    def test_UserOK2(self):
        """
        : param user : meth : : return :

        Args:
            self: (todo): write your description
        """
        julia = self.login("julia")
        num_petitions = julia.petition_set.count()

        response = self.client.get(reverse("user_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "petition/user_dashboard.html")
        self.assertTemplateUsed(response, "petition/user_base.html")
        self.assertTemplateUsed(response, "layouts/base.html")
        petitions = response.context['petitions'].all()
        self.assertEqual(len(petitions), num_petitions)
        self.assertEqual(response.context['user'], julia)

    def test_UserOK3(self):
        """
        Test if user hashed.

        Args:
            self: (todo): write your description
        """
        max = self.login("max")
        num_petitions = max.petition_set.count()

        response = self.client.get(reverse("user_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "petition/user_dashboard.html")
        self.assertTemplateUsed(response, "petition/user_base.html")
        self.assertTemplateUsed(response, "layouts/base.html")
        petitions = response.context['petitions'].all()
        self.assertEqual(len(petitions), num_petitions)
        self.assertEqual(response.context['user'], max)

    def test_UserOK4(self):
        """
        Respond to login a user.

        Args:
            self: (todo): write your description
        """
        sarah = self.login("sarah")
        num_petitions = sarah.petition_set.count()

        response = self.client.get(reverse("user_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "petition/user_dashboard.html")
        self.assertTemplateUsed(response, "petition/user_base.html")
        self.assertTemplateUsed(response, "layouts/base.html")
        petitions = response.context['petitions'].all()
        self.assertEqual(len(petitions), num_petitions)
        self.assertEqual(response.context['user'], sarah)
