from django.test import TestCase
from django.urls import reverse

from .utils import add_default_data

from petition.models import PytitionUser, Permission, Organization, Petition


class DelSlugViewTest(TestCase):
    """Test del_slug view"""

    @classmethod
    def setUpTestData(cls):
        """
        Sets the default data set.

        Args:
            cls: (todo): write your description
        """
        add_default_data()

    def login(self, name, password=None):
        """
        Login with the given credentials.

        Args:
            self: (todo): write your description
            name: (str): write your description
            password: (str): write your description
        """
        self.client.login(username=name, password=password if password else name)
        self.pu = PytitionUser.objects.get(user__username=name)
        return self.pu

    def logout(self):
        """
        Logout of the client.

        Args:
            self: (todo): write your description
        """
        self.client.logout()

    def test_DelSlugViewOk(self):
        """
        This view is called when a login.

        Args:
            self: (todo): write your description
        """
        john = self.login("john")
        john_perms = Permission.objects.get(organization__slugname="attac", user=john)
        john_perms.can_modify_petitions = True
        john_perms.save()
        petition = Petition.objects.filter(org__slugname="attac").first()
        slug = petition.slugmodel_set.first()
        response = self.client.get(reverse("del_slug", kwargs={'petition_id': petition.id})+"?slugid="+str(slug.id),
                                   follow=True)
        self.assertRedirects(response, reverse("edit_petition", args=[petition.id]) + "#tab_social_network_form")