from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from petition.models import Petition, PytitionUser, Signature

import random
import string

class SympaBlockTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        u = User.objects.create_user('julia', password='julia')

    def login(self, name, password=None):
        self.client.login(username=name, password=password if password else name)
        self.pu = PytitionUser.objects.get(user__username=name)
        return self.pu

    def logout(self):
        self.client.logout()

    def create_signatures(self, petition):
        self.nb_subscribed = 0
        for i in range(10):
            firstname = ''.join([random.choice(string.ascii_letters) for n in range(7)])
            lastname = ''.join([random.choice(string.ascii_letters) for n in range(7)])
            subscribed = False
            if i % 2:
                subscribed = True
                self.nb_subscribed = self.nb_subscribed + 1
            Signature.objects.create(
                first_name=firstname.capitalize(),
                last_name=lastname.capitalize(),
                email=f'{firstname}@{lastname}.net',
                petition=petition,
                confirmed=True,
                subscribed_to_mailinglist=subscribed
            )

    def test_ShowSympaSubscribeBlock(self):
        pu = self.login("julia")
        p = Petition.objects.create(title="my test petition", user=pu)
        self.create_signatures(p)
        response = self.client.get(reverse("show_sympa_subscribe_bloc", args=[p.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<br>", self.nb_subscribed)
        self.assertEqual(self.nb_subscribed, 5)
        for s in p.signature_set.all():
            if not s.confirmed or not s.subscribed_to_mailinglist:
                self.assertNotContains(response, f"{s.email} {s.first_name} {s.last_name}<br>\n")
            else:
                self.assertContains(response, f"{s.email} {s.first_name} {s.last_name}<br>\n", 1)