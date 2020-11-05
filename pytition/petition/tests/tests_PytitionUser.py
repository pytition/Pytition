from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from petition.models import Organization, Petition, PytitionUser, SlugModel


class PytitionUserTest(TestCase):
    def setUp(self):
        """
        Sets the result of this thread.

        Args:
            self: (todo): write your description
        """
        pass

    def test_createPytitionUser(self):
        """
        Creates a new test for use with pytition.

        Args:
            self: (todo): write your description
        """
        User = get_user_model()
        u = User.objects.create_user('julia', password='julia')
        self.assertEqual(PytitionUser.objects.count(), 1)
