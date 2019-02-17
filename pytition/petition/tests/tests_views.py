from django.test import TestCase
from petition.models import Organization, Petition

orgs = ['RAP', 'Greenpeace', 'Attac']
org_published_petitions = {
    'RAP': 0,
    'Les Amis de la Terre': 0,
    'Greenpeace': 1,
    'Attac': 2
}

org_unpublished_petitions = {
    'RAP': 0,
    'Les Amis de la Terre': 1,
    'Greenpeace': 0,
    'Attac': 2
}

class ViewsTest(TestCase):
    """Test views"""
    @classmethod
    def setUpTestData(cls):
        for org in orgs:
            o = Organization.objects.create(name=org)
            for i in range(org_published_petitions[org]):
                p = Petition.objects.create(published=True)
                o.petitions.add(p)
                p.save()
            for i in range(org_unpublished_petitions[org]):
                p = Petition.objects.create(published=False)
                o.petitions.add(p)
                p.save()
            o.save()


    def tearDown(self):
        # Clean up run after every test method.
        pass

    def test_index_all_petition(self):
        total_published_petitions = sum(org_published_petitions.values())
        with self.settings(INDEX_PAGE="ALL_PETITIONS"):
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.context['petitions']), total_published_petitions)

    def test_index_orga_petitions(self):
        for org in orgs:
            with self.settings(INDEX_PAGE="ORGA_PETITIONS", INDEX_PAGE_ORGA=org):
                response = self.client.get('/')
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response.context['petitions']), org_published_petitions[org])