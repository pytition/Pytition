from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from petition.models import Organization, Petition, PytitionUser, SlugModel, Signature, PetitionTemplate


class PetitionTemplateTest(TestCase):
    def setUp(self):
        User = get_user_model()
        u = User.objects.create_user('julia', password='julia')
        org = Organization.objects.create(name="RAP")

    def test_createUserPetitionTemplate(self):
        self.assertEqual(PetitionTemplate.objects.count(), 0)
        pu = PytitionUser.objects.get(user__username='julia')
        PetitionTemplate.objects.create(name="Default", user=pu)
        self.assertEqual(PetitionTemplate.objects.count(), 1)

    def test_createOrgPetitionTemplate(self):
        self.assertEqual(PetitionTemplate.objects.count(), 0)
        org = Organization.objects.first()
        PetitionTemplate.objects.create(name="Default", org=org)
        self.assertEqual(PetitionTemplate.objects.count(), 1)

    def test_createPetitionTemplateRefused(self):
        org = Organization.objects.first()
        pu = PytitionUser.objects.get(user__username='julia')
        self.assertEqual(PetitionTemplate.objects.count(), 0)
        self.assertRaises(Exception, PetitionTemplate.objects.create, name="PetitionTemplate")
        self.assertEqual(PetitionTemplate.objects.count(), 0)
        self.assertRaises(Exception, PetitionTemplate.objects.create, name="PetitionTemplate", user=pu, org=org)
        self.assertEqual(PetitionTemplate.objects.count(), 0)

    def test_owner_type(self):
        org = Organization.objects.first()
        pu = PytitionUser.objects.get(user__username='julia')
        p1 = PetitionTemplate.objects.create(name="PetitionTemplate", org=org)
        self.assertEqual('org', p1.owner_type)
        p2 = PetitionTemplate.objects.create(name="PetitionTemplate", user=pu)
        self.assertEqual('user', p2.owner_type)
