from django.test import TestCase
from django.urls import reverse

from .utils import add_default_data

from petition.models import Organization, Petition, PytitionUser


class PetitionViewTest(TestCase):
    """Test index view"""
    @classmethod
    def setUpTestData(cls):
        add_default_data()

    def tearDown(self):
        # Clean up run after every test method.
        pass

    def login(self, name, password=None):
        self.client.login(username=name, password=password if password else name)
        self.pu = PytitionUser.objects.get(user__username=name)
        return self.pu

    def logout(self):
        self.client.logout()

    def test_petition_detail(self):
        """ every body should see the petition, even when not logged in """
        petition = Petition.objects.filter(user__user__username="julia").first()
        response = self.client.get(reverse("detail", args=[petition.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['petition'], petition)
        self.assertTemplateUsed(response, "petition/petition_detail.html")

        self.assertContains(response, text='<meta property="og:site_name" content="testserver" />')
        self.assertContains(response, text='<meta property="og:url" content="http://testserver/petition/{}/" />'
                            .format(petition.id))

    def test_petition_success_msg(self):
        """ Test that the success modal is there when signing and confirming """
        petition = Petition.objects.filter(published=True).first()
        data = {
            'first_name': 'test first name',
            'last_name': 'test last name',
            'phone': '0123456789',
            'email': 'toto@toto.com'
        }
        # First, let's sign the petition
        response = self.client.post(reverse("create_signature", args=[petition.id]), data, follow=True)
        self.assertRedirects(response, petition.url)
        self.assertContains(response, text="""<script type="text/javascript">
$("#show_sign_success").modal("show");
</script>""")
        self.assertContains(response, text='<div class="modal fade" id="show_sign_success">')
        self.assertNotContains(response, text='show_confirm_success')
        # Now, let's confirm our signature
        signature = petition.signature_set.first()
        self.assertFalse(signature.confirmed)
        response = self.client.post(reverse("confirm", args=[petition.id, signature.confirmation_hash]), follow=True)
        self.assertRedirects(response, petition.url)
        signature.refresh_from_db()
        self.assertTrue(signature.confirmed)
        self.assertContains(response, text="""<script type="text/javascript">
$("#show_confirm_success").modal("show");
</script>""")
        self.assertContains(response, text='<div class="modal fade" id="show_confirm_success">')
        self.assertNotContains(response, text='show_sign_success')

    def test_petition_publish(self):
        self.logout()
        petition = Petition.objects.filter(user__user__username="julia").first()
        petition.published = False
        petition.save()
        self.assertEqual(petition.published, False)
        response = self.client.get(reverse("petition_publish", args=[petition.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(petition.published, False)
        self.login('julia')
        # Logged in with same user
        response = self.client.get(reverse("petition_publish", args=[petition.id]))
        self.assertEqual(response.status_code, 200)
        petition.refresh_from_db()
        self.assertEqual(petition.published, True)
        # Petition for another user
        john = PytitionUser.objects.get(user__username='john')
        p2 = Petition.objects.create(title='Pas content', user=john)
        self.assertEqual(p2.published, False)
        response = self.client.get(reverse("petition_publish", args=[p2.id]))
        p2.refresh_from_db()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(p2.published, False)
        # Petition from another organisation
        greenpeace = Organization.objects.get(name='Greenpeace')
        p3 = Petition.objects.create(title='Sauver la planete', org=greenpeace)
        self.assertEqual(p3.published, False)
        p3.refresh_from_db()
        response = self.client.get(reverse("petition_publish", args=[p3.id]))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(p3.published, False)

    def test_petition_unpublish(self):
        petition = Petition.objects.filter(user__user__username="julia").first()
        self.assertEqual(petition.published, True)
        self.logout()
        response = self.client.get(reverse("petition_unpublish", args=[petition.id]))
        petition.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(petition.published, True)
        # Test to unpublish from wrong user
        self.login("max")
        response = self.client.get(reverse("petition_unpublish", args=[petition.id]))
        petition.refresh_from_db()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(petition.published, True)
        self.login('julia')
        response = self.client.get(reverse("petition_unpublish", args=[petition.id]))
        petition.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(petition.published, False)

    def test_user_petition_delete(self):
        petitions = Petition.objects.filter(user__user__username="julia")
        petition = petitions.first()
        nb_julia_petitions = petitions.count()
        self.assertEqual(petitions.count(), nb_julia_petitions)
        response = self.client.get(reverse("petition_delete", args=[petition.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(petitions.count(), nb_julia_petitions)
        self.login('julia')
        response = self.client.get(reverse("petition_delete", args=[petition.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(petitions.count(), nb_julia_petitions - 1)

    def test_org_petition_delete(self):
        self.logout()
        petitions = Petition.objects.filter(org__name="Attac")
        petition = petitions.first()
        nb_attac_petitions = petitions.count()
        response = self.client.get(reverse("petition_delete", args=[petition.id]), follow=True)
        self.assertRedirects(response, reverse("login")+"?next="+reverse("petition_delete", args=[petition.id]))
        self.assertEqual(petitions.count(), nb_attac_petitions)
        self.login("john")
        response = self.client.get(reverse("petition_delete", args=[petition.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(petitions.count(), nb_attac_petitions - 1)

    def test_user_slug_show_petition(self):
        petition = Petition.objects.filter(user__user__username="julia").first()
        slug = petition.slugmodel_set.first().slug
        response = self.client.get(reverse("slug_show_petition", args=[petition.user.username, slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "petition/petition_detail.html")

    def pending_org_slug_show_petition(self):
        # Problem here
        org = Organization.objects.first()
        petition = Petition.objects.create(title="NON NON NON", org=org)
        slug = petition.slugmodel_set.first().slug
        response = self.client.get(reverse("slug_show_petition", args=[petition.org.slugname, slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "petition/petition_detail.html")

    def test_petition_publish_org(self):
        self.logout()
        petition = Petition.objects.filter(org__name="Les Amis de la Terre").first()
        petition.published = False
        petition.save()
        self.assertEqual(petition.published, False)
        response = self.client.get(reverse("petition_publish", args=[petition.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(petition.published, False)
        self.login('julia')
        # Logged in with same user
        response = self.client.get(reverse("petition_publish", args=[petition.id]))
        self.assertEqual(response.status_code, 200)
        petition.refresh_from_db()
        self.assertEqual(petition.published, True)
        # Petition from your org
        at = Organization.objects.get(name="Les Amis de la Terre")
        p2 = Petition.objects.create(title='Pas content', org=at)
        self.assertEqual(p2.published, False)
        response = self.client.get(reverse("petition_publish", args=[p2.id]))
        p2.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(p2.published, True)
        # Petition from your org, but with no right
        p2.published = False
        p2.save()
        self.logout()
        self.login("max")
        response = self.client.get(reverse("petition_publish", args=[p2.id]))
        p2.refresh_from_db()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(p2.published, False)
        # Petition from another organisation
        greenpeace = Organization.objects.get(name='Greenpeace')
        p3 = Petition.objects.create(title='Sauver la planete', org=greenpeace)
        self.assertEqual(p3.published, False)
        p3.refresh_from_db()
        response = self.client.get(reverse("petition_publish", args=[p3.id]))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(p3.published, False)

    def test_petition_unpublish_org(self):
        petition = Petition.objects.filter(org__name="Les Amis de la Terre").first()
        petition.published = True
        petition.save()
        self.logout()
        response = self.client.get(reverse("petition_unpublish", args=[petition.id]))
        petition.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(petition.published, True)
        self.login('julia')
        response = self.client.get(reverse("petition_unpublish", args=[petition.id]))
        petition.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(petition.published, False)
        petition.published = True
        petition.save()
        self.logout()
        self.login("max")
        response = self.client.get(reverse("petition_unpublish", args=[petition.id]))
        petition.refresh_from_db()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(petition.published, True)
        self.logout()
        self.login("sarah")
        response = self.client.get(reverse("petition_unpublish", args=[petition.id]))
        petition.refresh_from_db()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(petition.published, True)