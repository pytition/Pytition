from django.test import TestCase
from django.urls import reverse

import json

from .utils import add_default_data
from petition.models import PytitionUser


class GetUserListViewTest(TestCase):
    """Test get_user_list view"""

    @classmethod
    def setUpTestData(cls):
        add_default_data()

    def login(self, name, password=None):
        self.client.login(username=name, password=password if password else name)
        self.pu = PytitionUser.objects.get(user__username=name)
        return self.pu

    def test_GetUserListViewOk(self):
        self.login("julia")
        response = self.client.get(reverse('get_user_list')+"?q=admin")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], "application/json")
        values = response.json()['values']
        self.assertEquals(len(values), 1)
        self.assertEquals(values[0], "admin")

    def test_GetUserListViewEmptySearchOk(self):
        self.login("julia")
        response = self.client.get(reverse('get_user_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], "application/json")
        values = response.json()['values']
        self.assertEquals(len(values), 0)

    def test_GetUserListViewEmptyStringSearchOk(self):
        self.login("julia")
        response = self.client.get(reverse('get_user_list')+"?q=")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], "application/json")
        values = response.json()['values']
        self.assertEquals(len(values), 0)
