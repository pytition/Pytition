from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from petition.models import Organization, Petition, PytitionUser, SlugModel, Signature, Permission


class SignatureTest(TestCase):
    def setUp(self):
        User = get_user_model()
        u = User.objects.create_user('julia', password='julia')
        org = Organization.objects.create(name="RAP")
        pu = PytitionUser.objects.get(user__username='julia')
        Petition.objects.create(title="Petition", user=pu)

    def test_createSignature(self):
        p = Petition.objects.get(title="Petition")
        self.assertEqual(Signature.objects.count(), 0)
        s = Signature.objects.create(first_name="User", last_name="User", email="user@example.org", petition=p)
        self.assertEqual(Signature.objects.count(), 1)

    def pending_signature_requires(self):
        p = Petition.objects.get(title="Petition")
        # A signature requires a petition
        self.assertRaises(Signature.petition.RelatedObjectDoesNotExist, Signature.objects.create, first_name="User", last_name="User", email="user@example.org")
        s = Signature.objects.create(first_name="User", last_name="User", petition=p)
        self.assertEqual(Signature.objects.count(), 0)

    def pending_signature_should_be_uniq(self):
        org = Organization.objects.first()
        p1 = Petition.objects.get(title="Petition")
        #p2 = Petition.objects.create(title="Petition2", org=org)
        s1 = Signature.objects.create(first_name="User", last_name="User", email="user@example.org", petition=p1)
        s2 = Signature.objects.create(first_name="User", last_name="User", email="user@example.org", petition=p1)


