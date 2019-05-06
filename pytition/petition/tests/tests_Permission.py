import django
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from petition.models import Organization, Petition, PytitionUser, SlugModel, Signature, PetitionTemplate, Permission


class PermissionTest(TestCase):
    def setUp(self):
        User = get_user_model()
        u = User.objects.create_user('julia', password='julia')
        org = Organization.objects.create(name="RAP")

    def test_createPermission(self):
        self.assertEqual(Permission.objects.count(), 0)
        org = Organization.objects.get(name="RAP")
        pu = PytitionUser.objects.get(user__username='julia')
        org.members.add(pu)
        self.assertEqual(Permission.objects.count(), 1)
        p = Permission.objects.first()
        # By default set the following values
        self.assertEqual(p.can_add_members, False)
        self.assertEqual(p.can_remove_members, False)
        self.assertEqual(p.can_create_petitions, True)
        self.assertEqual(p.can_modify_petitions, True)
        self.assertEqual(p.can_delete_petitions, False)
        self.assertEqual(p.can_create_templates, True)
        self.assertEqual(p.can_modify_templates, True)
        self.assertEqual(p.can_delete_templates, False)
        self.assertEqual(p.can_view_signatures, False)
        self.assertEqual(p.can_modify_signatures, False)
        self.assertEqual(p.can_delete_signatures, False)
        self.assertEqual(p.can_modify_permissions, False)

    def test_to_string(self):
        self.assertEqual(Permission.objects.count(), 0)
        org = Organization.objects.get(name="RAP")
        pu = PytitionUser.objects.get(user__username='julia')
        org.members.add(pu)
        p = Permission.objects.first()
        self.assertEqual(str(p), "{} : {}".format(org.name, pu.name))
