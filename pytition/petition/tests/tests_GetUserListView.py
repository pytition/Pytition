from django.test import TestCase
from django.urls import reverse

import json

from .utils import add_default_data
from petition.models import PytitionUser


class GetUserListViewTest(TestCase):
    """Test get_user_list view"""

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

    def test_GetUserListViewOk(self):
        """
        Respond to get a user.

        Args:
            self: (todo): write your description
        """
        self.login("julia")
        response = self.client.get(reverse('get_user_list')+"?q=admin")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], "application/json")
        values = response.json()['values']
        self.assertEquals(len(values), 1)
        self.assertEquals(values[0], "admin")

    def test_GetUserListViewEmptySearchOk(self):
        """
        Called when the user is in the specified login.

        Args:
            self: (todo): write your description
        """
        self.login("julia")
        response = self.client.get(reverse('get_user_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], "application/json")
        values = response.json()['values']
        self.assertEquals(len(values), 0)

    def test_GetUserListViewEmptyStringSearchOk(self):
        """
        Returns the first search for a particular user.

        Args:
            self: (todo): write your description
        """
        self.login("julia")
        response = self.client.get(reverse('get_user_list')+"?q=")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], "application/json")
        values = response.json()['values']
        self.assertEquals(len(values), 0)
