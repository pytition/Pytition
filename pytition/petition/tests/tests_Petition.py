from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from petition.models import Organization, Petition, PytitionUser, SlugModel, Signature, Permission


class PetitionTest(TestCase):
    def setUp(self):
        User = get_user_model()
        u = User.objects.create_user('julia', password='julia')
        org = Organization.objects.create(name="RAP")

    def test_createUserPetition(self):
        self.assertEqual(Petition.objects.count(), 0)
        pu = PytitionUser.objects.get(user__username='julia')
        Petition.objects.create(title="Petition", user=pu)
        self.assertEqual(Petition.objects.count(), 1)

    def test_createOrgPetition(self):
        self.assertEqual(Petition.objects.count(), 0)
        org = Organization.objects.first()
        Petition.objects.create(title="Petition", org=org)
        self.assertEqual(Petition.objects.count(), 1)

    def test_createPetitionRefused(self):
        org = Organization.objects.first()
        pu = PytitionUser.objects.get(user__username='julia')
        self.assertEqual(Petition.objects.count(), 0)
        self.assertRaises(Exception, Petition.objects.create, title="Petition")
        self.assertEqual(Petition.objects.count(), 0)
        self.assertRaises(Exception, Petition.objects.create, title="Petition", user=pu, org=org)
        self.assertEqual(Petition.objects.count(), 0)

    def test_owner_type(self):
        org = Organization.objects.first()
        pu = PytitionUser.objects.get(user__username='julia')
        p1 = Petition.objects.create(title="Petition", org=org)
        self.assertEqual('org', p1.owner_type)
        p2 = Petition.objects.create(title="Petition", user=pu)
        self.assertEqual('user', p2.owner_type)

    def test_Petition_url(self):
        # If there is no slug, returns detail
        pu = PytitionUser.objects.get(user__username='julia')
        p = Petition.objects.create(title="Petition", user=pu)
        self.assertEqual(p.url, reverse('slug_show_petition', args=[pu.username, 'petition']))
        # This should never happen but testing just in case
        s = SlugModel.objects.first()
        s.delete()
        self.assertEqual(p.url, reverse('detail', args=[p.id]))
        # Create a slug
        #p.add_slug('foobar')

    def test_PetitionDelete(self):
        # Deleting a petition should delete related slugs and signatures
        pu = PytitionUser.objects.get(user__username='julia')
        p = Petition.objects.create(title="Petition", user=pu)
        self.assertEqual(Petition.objects.count(), 1)
        self.assertEqual(SlugModel.objects.count(), 1)
        p.delete()
        self.assertEqual(PytitionUser.objects.count(), 1)
        self.assertEqual(Petition.objects.count(), 0)
        self.assertEqual(SlugModel.objects.count(), 0)

    def testPetitionPublish(self):
        pu = PytitionUser.objects.get(user__username='julia')
        p = Petition.objects.create(title="Petition", user=pu)
        self.assertEqual(p.published, False)
        p.publish()
        self.assertEqual(p.published, True)
        p.unpublish()
        self.assertEqual(p.published, False)

    def test_autocreation_salt(self):
        pu = PytitionUser.objects.get(user__username='julia')
        p = Petition.objects.create(title="Petition", user=pu)
        self.assertIsNotNone(p.salt)
