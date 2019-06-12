from django.test import TestCase
from django.urls import reverse

from .utils import add_default_data

from petition.models import Petition, Signature, PytitionUser

class GetCsvSignatureViewTest(TestCase):
    """Test get_csv_signature view"""

    @classmethod
    def setUpTestData(cls):
        add_default_data()

    def login(self, name, password=None):
        self.client.login(username=name, password=password if password else name)
        self.pu = PytitionUser.objects.get(user__username=name)
        return self.pu

    def logout(self):
        self.client.logout()

    def test_GetCsvSignatureOk(self):
        julia = self.login('julia')
        petition = julia.petition_set.first()
        response = self.client.get(reverse('get_csv_signature', args=[petition.id]))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response['Content-Type'], 'text/csv')
        # TODO: add some csv parsing of the response

    def test_GetConfirmedSignatureOk(self):
        julia = self.login('julia')
        petition = julia.petition_set.first()
        response = self.client.get(reverse('get_csv_confirmed_signature', args=[petition.id]))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response['Content-Type'], 'text/csv')
        # TODO: add some csv parsing of the response