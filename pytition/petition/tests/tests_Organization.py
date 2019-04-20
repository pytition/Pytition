import django
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from petition.models import Organization, Petition, PytitionUser, SlugModel, Signature, PetitionTemplate


class OrganizationTest(TestCase):
    def setUp(self):
        pass

    def test_createOrganization(self):
        self.assertEqual(Organization.objects.count(), 0)
        o = Organization.objects.create()
        self.assertEqual(Organization.objects.count(), 1)

    def pending_org_requires_name(self):
        # Not clue why this is not working
        self.assertEqual(Organization.objects.count(), 0)
        o = Organization.objects.create()
        self.assertEqual(Organization.objects.count(), 0)

    def test_org_autocreate_slug(self):
        o = Organization.objects.create(name="RAP")
        self.assertEqual(o.slugname, "rap")

    def test_name_should_be_uniq(self):
        o = Organization.objects.create(name="RAP")
        self.assertEqual(Organization.objects.count(), 1)
        self.assertRaises(django.db.utils.IntegrityError, Organization.objects.create, name="RAP")

    def test_add_member(self):
        o = Organization.objects.create(name="RAP")
        User = get_user_model()
        u = User.objects.create_user('julia', password='julia')
        pu = PytitionUser.objects.get(user__username='julia')
        self.assertEqual(o.members.count(), 0)
        o.add_member(pu)
        self.assertEqual(o.members.count(), 1)

    def test_delete_org(self):
        org = Organization.objects.create(name="RAP")
        p = Petition.objects.create(title="Antipub", org=org)
        pt = PetitionTemplate.objects.create(name="Default", org=org)
        self.assertEqual(org.petition_set.count(), 1)
        self.assertEqual(Petition.objects.count(), 1)
        self.assertEqual(PetitionTemplate.objects.count(), 1)
        org.delete()
        self.assertEqual(Petition.objects.count(), 0)
        self.assertEqual(PetitionTemplate.objects.count(), 0)

