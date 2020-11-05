from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from petition.models import Organization, Petition, PytitionUser, SlugModel


class SlugModelTest(TestCase):
    def setUp(self):
        """
        Creates a user s password

        Args:
            self: (todo): write your description
        """
        User = get_user_model()
        u = User.objects.create_user('julia', password='julia')

    def test_autocreateSlug(self):
        """
        Test for auto - auto - auto - commit.

        Args:
            self: (todo): write your description
        """
        pu = PytitionUser.objects.get(user__username='julia')
        self.assertEqual(SlugModel.objects.count(), 0)
        p = Petition.objects.create(title="Petition1", user=pu)
        self.assertEqual(Petition.objects.count(), 1)
        self.assertEqual(SlugModel.objects.count(), 1)

    def test_createSlug(self):
        """
        Creates a new user

        Args:
            self: (todo): write your description
        """
        pu = PytitionUser.objects.get(user__username='julia')
        p = Petition.objects.create(title="Petition1", user=pu)
        self.assertEqual(Petition.objects.count(), 1)
        self.assertEqual(SlugModel.objects.count(), 1)
        p.add_slug('this-is-a-cool-slug')
        self.assertEqual(SlugModel.objects.count(), 2)

    def test_SlugShouldBeUniq(self):
        """
        Makes a user and creates a new model.

        Args:
            self: (todo): write your description
        """
        pu = PytitionUser.objects.get(user__username='julia')
        p = Petition.objects.create(title="Petition1", user=pu)
        self.assertEqual(Petition.objects.count(), 1)
        self.assertEqual(SlugModel.objects.count(), 1)
        p.add_slug('this-is-a-cool-slug')
        self.assertEqual(SlugModel.objects.count(), 2)
        #p.add_slug('this-is-a-cool-slug')
        self.assertRaises(ValueError, p.add_slug, 'this-is-a-cool-slug')
        self.assertEqual(SlugModel.objects.count(), 2)

    def test_SlugDelete(self):
        """
        Deletes a user.

        Args:
            self: (todo): write your description
        """
        pu = PytitionUser.objects.get(user__username='julia')
        p = Petition.objects.create(title="Petition1", user=pu)
        self.assertEqual(Petition.objects.count(), 1)
        self.assertEqual(SlugModel.objects.count(), 1)
        p.add_slug('this-is-a-cool-slug')
        self.assertEqual(SlugModel.objects.count(), 2)
        p.del_slug('this-is-a-cool-slug')
        self.assertEqual(SlugModel.objects.count(), 1)
