import logging
from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth.models import User

from petition.models import Organization, Permission, Petition, Signature

logging.disable(logging.CRITICAL)


class CommandTestCase(TestCase):
    def test_gen_orga_command(self):
        self.assertEqual(Organization.objects.count(), 0)

        call_command('gen_orga', 'test-org')
        self.assertEqual(Organization.objects.count(), 1)

        call_command('gen_orga', 'test-org')
        self.assertEqual(Organization.objects.count(), 1)

    def test_gen_user_command(self):
        self.assertEqual(User.objects.count(), 0)

        call_command('gen_user', 'user', 'password')
        self.assertEqual(User.objects.count(), 1)
        self.assertTrue(User.objects.first().check_password('password'))

        call_command('gen_user', 'user', 'password2', '--first-name', 'User')
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.first().first_name, 'User')
        self.assertTrue(User.objects.first().check_password('password2'))

    def test_join_org_command(self):
        org = Organization.objects.create(name="org")
        User.objects.create_user(username="user", password="pass")
        self.assertEqual(Permission.objects.count(), 0)
        self.assertEqual(org.members.count(), 0)

        call_command('join_org', 'user', 'org')
        self.assertEqual(Permission.objects.count(), 1)
        self.assertEqual(org.members.count(), 1)

        call_command('join_org', 'user2', 'org')
        self.assertEqual(Permission.objects.count(), 1)
        self.assertEqual(org.members.count(), 1)

        call_command('join_org', 'user', 'org2')
        self.assertEqual(Permission.objects.count(), 1)
        self.assertEqual(org.members.count(), 1)

    def test_gen_pet_command(self):
        Organization.objects.create(name="org")
        User.objects.create_user(username="user", password="pass")
        self.assertEqual(Petition.objects.count(), 0)

        call_command('gen_pet', '--user', 'user')
        self.assertEqual(Petition.objects.count(), 1)

        call_command('gen_pet', '--orga', 'org', '--number', '9')
        self.assertEqual(Petition.objects.count(), 10)

    def test_gen_sig_command(self):
        org = Organization.objects.create(name="org")
        user = User.objects.create_user(username="user", password="pass")
        pet = Petition.objects.create(title="Test", user=user.pytitionuser)
        self.assertEqual(Signature.objects.count(), 0)

        call_command('gen_sig', pet.id)
        self.assertEqual(Signature.objects.count(), 1)

        call_command('gen_sig', '2')
        self.assertEqual(Signature.objects.count(), 1)

        call_command('gen_sig', 'Test')
        self.assertEqual(Signature.objects.count(), 2)

        Petition.objects.create(title="Test", org=org)
        call_command('gen_sig', 'Test')
        self.assertEqual(Signature.objects.count(), 2)

        call_command('gen_sig', pet.id, '--number', '8')
        self.assertEqual(Signature.objects.count(), 10)
