from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from petition.models import Organization, Petition, PytitionUser, SlugModel, SlugOwnership


class PetitionTest(TestCase):
    def setUp(self):
        pass

    def test_createPetition(self):
        Petition.objects.create(title="Petition")
        self.assertEqual(Petition.objects.count(), 1)

    def test_Petition_url(self):
        # If there is no slug, returns detail
        User = get_user_model()
        u = User.objects.create_user('julia', password='julia')
        pu = PytitionUser.objects.get(user__username='julia')
        p = Petition.objects.create(title="Petition", )
        pu.petitions.add(p)
        self.assertEqual(p.url, reverse('detail', args=[p.id]))
        # Create a slug
        p.add_slug('foobar')
        self.assertEqual(p.url, reverse('slug_show_petition', args=[u.username, 'foobar']))
