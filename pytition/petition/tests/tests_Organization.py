import django
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from petition.models import Organization, Petition, PytitionUser, SlugModel, Signature, PetitionTemplate, Permission
from .utils import add_default_data


class OrganizationTest(TestCase):
    def setUp(self):
        pass

    def test_createOrganization(self):
        self.assertEqual(Organization.objects.count(), 0)
        o = Organization.objects.create()
        self.assertEqual(Organization.objects.count(), 1)

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
        o.members.add(pu)
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

    def test_is_last_admin(self):
        add_default_data()
        julia = PytitionUser.objects.get(user__username="julia")
        org = Organization.objects.get(name='Les Amis de la Terre')
        self.assertEqual(org.is_last_admin(julia), True)
        # Add another admin
        max = PytitionUser.objects.get(user__username="max")
        perm = Permission.objects.get(organization=org, user=max)
        perm.can_modify_permissions = True
        perm.save()
        self.assertEqual(org.is_last_admin(julia), False)

    def test_is_allowed_to(self):
        o = Organization.objects.create(name="RAP")
        User = get_user_model()
        u = User.objects.create_user('julia', password='julia')
        pu = PytitionUser.objects.get(user__username='julia')
        o.members.add(pu)
        self.assertEqual(o.is_allowed_to(pu, 'can_add_members'), False)
        self.assertEqual(o.is_allowed_to(pu, 'can_remove_members'), False)
        self.assertEqual(o.is_allowed_to(pu, 'can_create_petitions'), True)
        self.assertEqual(o.is_allowed_to(pu, 'can_modify_petitions'), True)
        self.assertEqual(o.is_allowed_to(pu, 'can_delete_petitions'), False)
        self.assertEqual(o.is_allowed_to(pu, 'can_create_templates'), True)
        self.assertEqual(o.is_allowed_to(pu, 'can_modify_templates'), True)
        self.assertEqual(o.is_allowed_to(pu, 'can_delete_templates'), False)
        self.assertEqual(o.is_allowed_to(pu, 'can_view_signatures'), False)
        self.assertEqual(o.is_allowed_to(pu, 'can_modify_signatures'), False)
        self.assertEqual(o.is_allowed_to(pu, 'can_delete_signatures'), False)
        self.assertEqual(o.is_allowed_to(pu, 'can_modify_permissions'), False)
