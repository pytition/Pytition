from django.test import TestCase
from django.urls import reverse

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
