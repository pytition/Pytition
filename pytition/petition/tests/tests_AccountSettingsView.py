from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from petition.models import Organization, Petition, PytitionUser, Permission
from petition.helpers import get_update_form
from petition.forms import DeleteAccountForm
from .utils import add_default_data


class AccountSettingsViewTest(TestCase):
    """Test index view"""
    @classmethod
    def setUpTestData(cls):
        add_default_data()

    def login(self, name, password=None):
        self.client.login(username=name, password=password if password else name)
        self.pu = PytitionUser.objects.get(user__username=name)
        return self.pu

    def logout(self):
        self.client.logout()

    def tearDown(self):
        # Clean up run after every test method.
        pass

    def test_NotLoggedIn(self):
        self.logout()
        response = self.client.get(reverse("account_settings"), follow=True)
        self.assertRedirects(response, reverse("login")+"?next="+reverse("account_settings"))
        self.assertTemplateUsed(response, "registration/login.html")
        self.assertTemplateUsed(response, "layouts/base.html")

    def test_UserOK1(self):
        john = self.login("john")
        update_info_form = get_update_form(john.user)

        response = self.client.get(reverse("account_settings"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "petition/account_settings.html")
        self.assertTemplateUsed(response, "layouts/base.html")
        self.assertEqual(response.context['user'], john)
        self.assertEqual(response.context['update_info_form_submitted'], False)
        self.assertEqual(response.context['delete_account_form_submitted'], False)
        self.assertEqual(response.context['password_change_form_submitted'], False)
        self.assertEqual(response.context['update_info_form'].is_valid(), True)
        self.assertEqual(response.context['update_info_form'].is_bound, True)
        self.assertEqual(response.context['delete_account_form'].is_valid(), False)
        self.assertEqual(response.context['delete_account_form'].is_bound, False)
        self.assertEqual(response.context['password_change_form'].is_valid(), False)
        self.assertEqual(response.context['password_change_form'].is_bound, False)

    def test_UserOK2(self):
        julia = self.login("julia")

        response = self.client.get(reverse("account_settings"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "petition/account_settings.html")
        self.assertTemplateUsed(response, "layouts/base.html")
        self.assertEqual(response.context['user'], julia)
        self.assertEqual(response.context['update_info_form_submitted'], False)
        self.assertEqual(response.context['delete_account_form_submitted'], False)
        self.assertEqual(response.context['password_change_form_submitted'], False)
        self.assertEqual(response.context['update_info_form'].is_valid(), True)
        self.assertEqual(response.context['update_info_form'].is_bound, True)
        self.assertEqual(response.context['delete_account_form'].is_valid(), False)
        self.assertEqual(response.context['delete_account_form'].is_bound, False)
        self.assertEqual(response.context['password_change_form'].is_valid(), False)
        self.assertEqual(response.context['password_change_form'].is_bound, False)

    def test_UserOK3(self):
        max = self.login("max")
        response = self.client.get(reverse("account_settings"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "petition/account_settings.html")
        self.assertTemplateUsed(response, "layouts/base.html")
        self.assertEqual(response.context['user'], max)
        self.assertEqual(response.context['update_info_form_submitted'], False)
        self.assertEqual(response.context['delete_account_form_submitted'], False)
        self.assertEqual(response.context['password_change_form_submitted'], False)
        self.assertEqual(response.context['update_info_form'].is_valid(), True)
        self.assertEqual(response.context['update_info_form'].is_bound, True)
        self.assertEqual(response.context['delete_account_form'].is_valid(), False)
        self.assertEqual(response.context['delete_account_form'].is_bound, False)
        self.assertEqual(response.context['password_change_form'].is_valid(), False)
        self.assertEqual(response.context['password_change_form'].is_bound, False)

    def test_UserOK4(self):
        sarah = self.login("sarah")
        response = self.client.get(reverse("account_settings"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "petition/account_settings.html")
        self.assertTemplateUsed(response, "layouts/base.html")
        self.assertEqual(response.context['user'], sarah)
        self.assertEqual(response.context['update_info_form_submitted'], False)
        self.assertEqual(response.context['delete_account_form_submitted'], False)
        self.assertEqual(response.context['password_change_form_submitted'], False)
        self.assertEqual(response.context['update_info_form'].is_valid(), True)
        self.assertEqual(response.context['update_info_form'].is_bound, True)
        self.assertEqual(response.context['delete_account_form'].is_valid(), False)
        self.assertEqual(response.context['delete_account_form'].is_bound, False)
        self.assertEqual(response.context['password_change_form'].is_valid(), False)
        self.assertEqual(response.context['password_change_form'].is_bound, False)

    def test_UserjohnPOSTUserInfoOK(self):
        john = self.login("john")
        update_info_form = get_update_form(john.user)
        update_info_form.is_valid()
        data = update_info_form.cleaned_data
        data.update({
            'update_info_form_submitted': 'yes',
        })
        response = self.client.post(reverse("account_settings"), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "petition/account_settings.html")
        self.assertTemplateUsed(response, "layouts/base.html")
        self.assertEqual(response.context['user'], john)
        self.assertEqual(response.context['update_info_form_submitted'], True)
        self.assertEqual(response.context['delete_account_form_submitted'], False)
        self.assertEqual(response.context['password_change_form_submitted'], False)
        self.assertEqual(response.context['update_info_form'].is_valid(), True)
        self.assertEqual(response.context['update_info_form'].is_bound, True)
        self.assertEqual(response.context['delete_account_form'].is_valid(), False)
        self.assertEqual(response.context['delete_account_form'].is_bound, False)
        self.assertEqual(response.context['password_change_form'].is_valid(), False)
        self.assertEqual(response.context['password_change_form'].is_bound, False)

    def test_UserjohnPOSTPassChangeOK(self):
        john = self.login("john")
        new_pass = 'eytksjezu375&#'
        data = {
            'password_change_form_submitted': 'yes',
            'old_password': 'john',
            'new_password1': new_pass,
            'new_password2': new_pass,
        }
        response = self.client.post(reverse("account_settings"), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "petition/account_settings.html")
        self.assertTemplateUsed(response, "layouts/base.html")
        self.assertEqual(response.context['user'], john)
        self.assertEqual(response.context['update_info_form_submitted'], False)
        self.assertEqual(response.context['delete_account_form_submitted'], False)
        self.assertEqual(response.context['password_change_form_submitted'], True)
        self.assertEqual(response.context['update_info_form'].is_valid(), True)
        self.assertEqual(response.context['update_info_form'].is_bound, True)
        self.assertEqual(response.context['delete_account_form'].is_valid(), False)
        self.assertEqual(response.context['delete_account_form'].is_bound, False)
        self.assertEqual(response.context['password_change_form'].is_valid(), True)
        self.assertEqual(response.context['password_change_form'].is_bound, True)
        self.logout()
        self.login("john", password=new_pass)
        response2 = self.client.get(reverse("user_dashboard"))
        self.assertEqual(response2.status_code, 200)
        self.logout()
        self.login("john")
        response3 = self.client.get(reverse("user_dashboard"), follow=True)
        self.assertRedirects(response3, reverse("login")+"?next="+reverse("user_dashboard"))

    def test_UserjohnPOSTDeleteAccountOK(self):
        # to avoid 404 error when index page redirects to deleted Organization profile page
        with self.settings(INDEX_PAGE="ALL_PETITIONS"):
            self.login("john")
            data = {
                'validation': "DROP MY ACCOUNT",
                'delete_account_form_submitted': "yes",
            }
            f = DeleteAccountForm(data)
            self.assertEqual(f.is_valid(), True)
            response = self.client.post(reverse("account_settings"), data, follow=True)
            self.assertRedirects(response, reverse("all_petitions"))
            self.assertTemplateUsed(response, "layouts/base.html")
            self.logout()
            try:
                self.login("john")
                response2 = self.client.get(reverse("user_dashboard"))
                self.assertRedirects(response2, reverse("login")+"?next="+reverse("user_dashboard"))
                self.assertEqual(0, 1) # Should never be reached
            except:
                pass # I expected that!
            pu = PytitionUser.objects.filter(user__username="john").count()
            self.assertEqual(pu, 0)
            User = get_user_model()
            u = User.objects.filter(username="john").count()
            self.assertEqual(u, 0)

    def test_UsersarahPOSTUserInfoOK(self):
        username = "sarah"
        user = self.login(username)
        update_info_form = get_update_form(user.user)
        update_info_form.is_valid()
        data = update_info_form.cleaned_data
        data.update({
            'update_info_form_submitted': 'yes',
        })
        response = self.client.post(reverse("account_settings"), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "petition/account_settings.html")
        self.assertTemplateUsed(response, "layouts/base.html")
        self.assertEqual(response.context['user'], user)
        self.assertEqual(response.context['update_info_form_submitted'], True)
        self.assertEqual(response.context['delete_account_form_submitted'], False)
        self.assertEqual(response.context['password_change_form_submitted'], False)
        self.assertEqual(response.context['update_info_form'].is_valid(), True)
        self.assertEqual(response.context['update_info_form'].is_bound, True)
        self.assertEqual(response.context['delete_account_form'].is_valid(), False)
        self.assertEqual(response.context['delete_account_form'].is_bound, False)
        self.assertEqual(response.context['password_change_form'].is_valid(), False)
        self.assertEqual(response.context['password_change_form'].is_bound, False)

    def test_UsersarahPOSTPassChangeOK(self):
        username ="sarah"
        user = self.login(username)
        new_pass = 'eytksjezu375&#'
        data = {
            'password_change_form_submitted': 'yes',
            'old_password': username,
            'new_password1': new_pass,
            'new_password2': new_pass,
        }
        response = self.client.post(reverse("account_settings"), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "petition/account_settings.html")
        self.assertTemplateUsed(response, "layouts/base.html")
        self.assertEqual(response.context['user'], user)
        self.assertEqual(response.context['update_info_form_submitted'], False)
        self.assertEqual(response.context['delete_account_form_submitted'], False)
        self.assertEqual(response.context['password_change_form_submitted'], True)
        self.assertEqual(response.context['update_info_form'].is_valid(), True)
        self.assertEqual(response.context['update_info_form'].is_bound, True)
        self.assertEqual(response.context['delete_account_form'].is_valid(), False)
        self.assertEqual(response.context['delete_account_form'].is_bound, False)
        self.assertEqual(response.context['password_change_form'].is_valid(), True)
        self.assertEqual(response.context['password_change_form'].is_bound, True)
        self.logout()
        self.login(username, password=new_pass)
        response2 = self.client.get(reverse("user_dashboard"))
        self.assertEqual(response2.status_code, 200)
        self.logout()
        self.login(username)
        response3 = self.client.get(reverse("user_dashboard"), follow=True)
        self.assertRedirects(response3, reverse("login")+"?next="+reverse("user_dashboard"))

    def test_UsersarahPOSTDeleteAccountOK(self):
        # to avoid 404 error when index page redirects to deleted Organization profile page
        with self.settings(INDEX_PAGE="ALL_PETITIONS"):
            username = "sarah"
            self.login(username)
            data = {
                'validation': "DROP MY ACCOUNT",
                'delete_account_form_submitted': "yes",
            }
            f = DeleteAccountForm(data)
            self.assertEqual(f.is_valid(), True)
            response = self.client.post(reverse("account_settings"), data, follow=True)
            self.assertRedirects(response, reverse("all_petitions"))
            self.assertTemplateUsed(response, "layouts/base.html")
            self.logout()
            try:
                self.login(username)
                response2 = self.client.get(reverse("user_dashboard"))
                self.assertRedirects(response2, reverse("login")+"?next="+reverse("user_dashboard"))
                self.assertEqual(0, 1) # Should never be reached
            except:
                pass # I expected that!
            pu = PytitionUser.objects.filter(user__username=username).count()
            self.assertEqual(pu, 0)
            User = get_user_model()
            u = User.objects.filter(username=username).count()
            self.assertEqual(u, 0)

    def test_UserjuliaPOSTUserInfoOK(self):
        username = "julia"
        user = self.login(username)
        update_info_form = get_update_form(user.user)
        update_info_form.is_valid()
        data = update_info_form.cleaned_data
        data.update({
            'update_info_form_submitted': 'yes',
        })
        response = self.client.post(reverse("account_settings"), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "petition/account_settings.html")
        self.assertTemplateUsed(response, "layouts/base.html")
        self.assertEqual(response.context['user'], user)
        self.assertEqual(response.context['update_info_form_submitted'], True)
        self.assertEqual(response.context['delete_account_form_submitted'], False)
        self.assertEqual(response.context['password_change_form_submitted'], False)
        self.assertEqual(response.context['update_info_form'].is_valid(), True)
        self.assertEqual(response.context['update_info_form'].is_bound, True)
        self.assertEqual(response.context['delete_account_form'].is_valid(), False)
        self.assertEqual(response.context['delete_account_form'].is_bound, False)
        self.assertEqual(response.context['password_change_form'].is_valid(), False)
        self.assertEqual(response.context['password_change_form'].is_bound, False)

    def test_UserjuliaPOSTPassChangeOK(self):
        username ="julia"
        user = self.login(username)
        new_pass = 'eytksjezu375&#'
        data = {
            'password_change_form_submitted': 'yes',
            'old_password': username,
            'new_password1': new_pass,
            'new_password2': new_pass,
        }
        response = self.client.post(reverse("account_settings"), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "petition/account_settings.html")
        self.assertTemplateUsed(response, "layouts/base.html")
        self.assertEqual(response.context['user'], user)
        self.assertEqual(response.context['update_info_form_submitted'], False)
        self.assertEqual(response.context['delete_account_form_submitted'], False)
        self.assertEqual(response.context['password_change_form_submitted'], True)
        self.assertEqual(response.context['update_info_form'].is_valid(), True)
        self.assertEqual(response.context['update_info_form'].is_bound, True)
        self.assertEqual(response.context['delete_account_form'].is_valid(), False)
        self.assertEqual(response.context['delete_account_form'].is_bound, False)
        self.assertEqual(response.context['password_change_form'].is_valid(), True)
        self.assertEqual(response.context['password_change_form'].is_bound, True)
        self.logout()
        self.login(username, password=new_pass)
        response2 = self.client.get(reverse("user_dashboard"))
        self.assertEqual(response2.status_code, 200)
        self.logout()
        self.login(username)
        response3 = self.client.get(reverse("user_dashboard"), follow=True)
        self.assertRedirects(response3, reverse("login")+"?next="+reverse("user_dashboard"))

    def test_UserjuliaPOSTDeleteAccountOK(self):
        # to avoid 404 error when index page redirects to deleted Organization profile page
        with self.settings(INDEX_PAGE="ALL_PETITIONS"):
            username = "julia"
            self.login(username)
            data = {
                'validation': "DROP MY ACCOUNT",
                'delete_account_form_submitted': "yes",
            }
            f = DeleteAccountForm(data)
            self.assertEqual(f.is_valid(), True)
            response = self.client.post(reverse("account_settings"), data, follow=True)
            self.assertRedirects(response, reverse("all_petitions"))
            self.assertTemplateUsed(response, "layouts/base.html")
            self.logout()
            try:
                self.login(username)
                response2 = self.client.get(reverse("user_dashboard"))
                self.assertRedirects(response2, reverse("login")+"?next="+reverse("user_dashboard"))
                self.assertEqual(0, 1) # Should never be reached
            except:
                pass # I expected that!
            pu = PytitionUser.objects.filter(user__username=username).count()
            self.assertEqual(pu, 0)
            User = get_user_model()
            u = User.objects.filter(username=username).count()
            self.assertEqual(u, 0)

    def test_UsermaxPOSTUserInfoOK(self):
        username = "max"
        user = self.login(username)
        update_info_form = get_update_form(user.user)
        update_info_form.is_valid()
        data = update_info_form.cleaned_data
        data.update({
            'update_info_form_submitted': 'yes',
        })
        response = self.client.post(reverse("account_settings"), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "petition/account_settings.html")
        self.assertTemplateUsed(response, "layouts/base.html")
        self.assertEqual(response.context['user'], user)
        self.assertEqual(response.context['update_info_form_submitted'], True)
        self.assertEqual(response.context['delete_account_form_submitted'], False)
        self.assertEqual(response.context['password_change_form_submitted'], False)
        self.assertEqual(response.context['update_info_form'].is_valid(), True)
        self.assertEqual(response.context['update_info_form'].is_bound, True)
        self.assertEqual(response.context['delete_account_form'].is_valid(), False)
        self.assertEqual(response.context['delete_account_form'].is_bound, False)
        self.assertEqual(response.context['password_change_form'].is_valid(), False)
        self.assertEqual(response.context['password_change_form'].is_bound, False)

    def test_UsermaxPOSTPassChangeOK(self):
        username ="max"
        user = self.login(username)
        new_pass = 'eytksjezu375&#'
        data = {
            'password_change_form_submitted': 'yes',
            'old_password': username,
            'new_password1': new_pass,
            'new_password2': new_pass,
        }
        response = self.client.post(reverse("account_settings"), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "petition/account_settings.html")
        self.assertTemplateUsed(response, "layouts/base.html")
        self.assertEqual(response.context['user'], user)
        self.assertEqual(response.context['update_info_form_submitted'], False)
        self.assertEqual(response.context['delete_account_form_submitted'], False)
        self.assertEqual(response.context['password_change_form_submitted'], True)
        self.assertEqual(response.context['update_info_form'].is_valid(), True)
        self.assertEqual(response.context['update_info_form'].is_bound, True)
        self.assertEqual(response.context['delete_account_form'].is_valid(), False)
        self.assertEqual(response.context['delete_account_form'].is_bound, False)
        self.assertEqual(response.context['password_change_form'].is_valid(), True)
        self.assertEqual(response.context['password_change_form'].is_bound, True)
        self.logout()
        self.login(username, password=new_pass)
        response2 = self.client.get(reverse("user_dashboard"))
        self.assertEqual(response2.status_code, 200)
        self.logout()
        self.login(username)
        response3 = self.client.get(reverse("user_dashboard"), follow=True)
        self.assertRedirects(response3, reverse("login")+"?next="+reverse("user_dashboard"))

    def test_UsermaxPOSTDeleteAccountOK(self):
        with self.settings(INDEX_PAGE="ALL_PETITIONS"):
            username = "max"
            self.login(username)
            data = {
                'validation': "DROP MY ACCOUNT",
                'delete_account_form_submitted': "yes",
            }
            f = DeleteAccountForm(data)
            self.assertEqual(f.is_valid(), True)
            response = self.client.post(reverse("account_settings"), data, follow=True)
            self.assertRedirects(response, reverse("all_petitions"))
            self.assertTemplateUsed(response, "layouts/base.html")
            self.logout()
            try:
                self.login(username)
                response2 = self.client.get(reverse("user_dashboard"))
                self.assertRedirects(response2, reverse("login")+"?next="+reverse("user_dashboard"))
                self.assertEqual(0, 1) # Should never be reached
            except:
                pass # I expected that!
            pu = PytitionUser.objects.filter(user__username=username).count()
            self.assertEqual(pu, 0)
            User = get_user_model()
            u = User.objects.filter(username=username).count()
            self.assertEqual(u, 0)

    def test_UsermaxPOSTDeleteAccountValidNOK(self):
        username = "max"
        self.login(username)
        data = {
            'validation': "DO *NOT* DROP MY ACCOUNT",
            'delete_account_form_submitted': "yes",
        }
        f = DeleteAccountForm(data)
        self.assertEqual(f.is_valid(), False)
        response = self.client.post(reverse("account_settings"), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "layouts/base.html")
        self.assertTemplateUsed(response, "petition/account_settings.html")
        self.logout()
        self.login(username)
        response2 = self.client.get(reverse("user_dashboard"))
        self.assertEqual(response2.status_code, 200)
        pu = PytitionUser.objects.filter(user__username=username).count()
        self.assertEqual(pu, 1)
        User = get_user_model()
        u = User.objects.filter(username=username).count()
        self.assertEqual(u, 1)

    def test_UserjuliaPOSTDeleteAccountValidNOK(self):
        username = "julia"
        self.login(username)
        data = {
            'validation': "DO *NOT* DROP MY ACCOUNT",
            'delete_account_form_submitted': "yes",
        }
        f = DeleteAccountForm(data)
        self.assertEqual(f.is_valid(), False)
        response = self.client.post(reverse("account_settings"), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "layouts/base.html")
        self.assertTemplateUsed(response, "petition/account_settings.html")
        self.logout()
        self.login(username)
        response2 = self.client.get(reverse("user_dashboard"))
        self.assertEqual(response2.status_code, 200)
        pu = PytitionUser.objects.filter(user__username=username).count()
        self.assertEqual(pu, 1)
        User = get_user_model()
        u = User.objects.filter(username=username).count()
        self.assertEqual(u, 1)

    def test_UserjohnPOSTDeleteAccountValidNOK(self):
        username = "john"
        self.login(username)
        data = {
            'validation': "DO *NOT* DROP MY ACCOUNT",
            'delete_account_form_submitted': "yes",
        }
        f = DeleteAccountForm(data)
        self.assertEqual(f.is_valid(), False)
        response = self.client.post(reverse("account_settings"), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "layouts/base.html")
        self.assertTemplateUsed(response, "petition/account_settings.html")
        self.logout()
        self.login(username)
        response2 = self.client.get(reverse("user_dashboard"))
        self.assertEqual(response2.status_code, 200)
        pu = PytitionUser.objects.filter(user__username=username).count()
        self.assertEqual(pu, 1)
        User = get_user_model()
        u = User.objects.filter(username=username).count()
        self.assertEqual(u, 1)


    def test_UsersarahPOSTDeleteAccountValidNOK(self):
        username = "sarah"
        self.login(username)
        data = {
            'validation': "DO *NOT* DROP MY ACCOUNT",
            'delete_account_form_submitted': "yes",
        }
        f = DeleteAccountForm(data)
        self.assertEqual(f.is_valid(), False)
        response = self.client.post(reverse("account_settings"), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "layouts/base.html")
        self.assertTemplateUsed(response, "petition/account_settings.html")
        self.logout()
        self.login(username)
        response2 = self.client.get(reverse("user_dashboard"))
        self.assertEqual(response2.status_code, 200)
        pu = PytitionUser.objects.filter(user__username=username).count()
        self.assertEqual(pu, 1)
        User = get_user_model()
        u = User.objects.filter(username=username).count()
        self.assertEqual(u, 1)

    def test_UserUnauthenticatedPOST(self):
        self.logout()
        data = {
            'validation': "DROP MY ACCOUNT",
            'delete_account_form_submitted': "yes",
        }
        f = DeleteAccountForm(data)
        self.assertEqual(f.is_valid(), True)
        response = self.client.post(reverse("account_settings"), data, follow=True)
        self.assertRedirects(response, reverse("login")+"?next="+reverse("account_settings"))
        self.assertTemplateUsed(response, "layouts/base.html")

    def test_UserUnauthenticatedGET(self):
        self.logout()
        response = self.client.get(reverse("account_settings"), follow=True)
        self.assertRedirects(response, reverse("login")+"?next="+reverse("account_settings"))
        self.assertTemplateUsed(response, "layouts/base.html")

    def test_UsermaxPOSTUpdateUserInfoEmailKO(self):
        username = "max"
        user = self.login(username)
        initial_data = {
            'first_name': user.user.first_name,
            'last_name': user.user.last_name,
            'email': "wrongEmailSyntax",
        }
        update_info_form = get_update_form(user.user, data=initial_data)
        update_info_form.is_valid()
        self.assertEqual(update_info_form.is_valid(), False)
        data = update_info_form.cleaned_data
        data.update({
            'update_info_form_submitted': 'yes',
            'email': "wrongEmailSyntax",
        })
        response = self.client.post(reverse("account_settings"), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "petition/account_settings.html")
        self.assertTemplateUsed(response, "layouts/base.html")
        self.assertEqual(response.context['user'], user)
        self.assertEqual(response.context['update_info_form_submitted'], True)
        self.assertEqual(response.context['delete_account_form_submitted'], False)
        self.assertEqual(response.context['password_change_form_submitted'], False)
        self.assertEqual(response.context['update_info_form'].is_valid(), False)
        self.assertEqual(response.context['update_info_form'].is_bound, True)
        self.assertEqual(response.context['delete_account_form'].is_valid(), False)
        self.assertEqual(response.context['delete_account_form'].is_bound, False)
        self.assertEqual(response.context['password_change_form'].is_valid(), False)
        self.assertEqual(response.context['password_change_form'].is_bound, False)
        new_update_info_form = response.context['update_info_form']
        self.assertIn('password_mismatch', new_update_info_form.error_messages)
        self.assertIn('email', new_update_info_form.errors)

    def test_UsersarahPOSTUpdateUserInfoEmailKO(self):
        username = "sarah"
        user = self.login(username)
        initial_data = {
            'first_name': user.user.first_name,
            'last_name': user.user.last_name,
            'email': "wrongEmailSyntax",
        }
        update_info_form = get_update_form(user.user, data=initial_data)
        update_info_form.is_valid()
        self.assertEqual(update_info_form.is_valid(), False)
        data = update_info_form.cleaned_data
        data.update({
            'update_info_form_submitted': 'yes',
            'email': "wrongEmailSyntax",
        })
        response = self.client.post(reverse("account_settings"), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "petition/account_settings.html")
        self.assertTemplateUsed(response, "layouts/base.html")
        self.assertEqual(response.context['user'], user)
        self.assertEqual(response.context['update_info_form_submitted'], True)
        self.assertEqual(response.context['delete_account_form_submitted'], False)
        self.assertEqual(response.context['password_change_form_submitted'], False)
        self.assertEqual(response.context['update_info_form'].is_valid(), False)
        self.assertEqual(response.context['update_info_form'].is_bound, True)
        self.assertEqual(response.context['delete_account_form'].is_valid(), False)
        self.assertEqual(response.context['delete_account_form'].is_bound, False)
        self.assertEqual(response.context['password_change_form'].is_valid(), False)
        self.assertEqual(response.context['password_change_form'].is_bound, False)
        new_update_info_form = response.context['update_info_form']
        self.assertIn('password_mismatch', new_update_info_form.error_messages)
        self.assertIn('email', new_update_info_form.errors)

    def test_UserjohnPOSTUpdateUserInfoEmailKO(self):
        username = "john"
        user = self.login(username)
        initial_data = {
            'first_name': user.user.first_name,
            'last_name': user.user.last_name,
            'email': "wrongEmailSyntax",
        }
        update_info_form = get_update_form(user.user, data=initial_data)
        update_info_form.is_valid()
        self.assertEqual(update_info_form.is_valid(), False)
        data = update_info_form.cleaned_data
        data.update({
            'update_info_form_submitted': 'yes',
            'email': "wrongEmailSyntax", # We put it again because invalid values are not part of cleaned_data
        })
        response = self.client.post(reverse("account_settings"), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "petition/account_settings.html")
        self.assertTemplateUsed(response, "layouts/base.html")
        self.assertEqual(response.context['user'], user)
        self.assertEqual(response.context['update_info_form_submitted'], True)
        self.assertEqual(response.context['delete_account_form_submitted'], False)
        self.assertEqual(response.context['password_change_form_submitted'], False)
        self.assertEqual(response.context['update_info_form'].is_valid(), False)
        self.assertEqual(response.context['update_info_form'].is_bound, True)
        self.assertEqual(response.context['delete_account_form'].is_valid(), False)
        self.assertEqual(response.context['delete_account_form'].is_bound, False)
        self.assertEqual(response.context['password_change_form'].is_valid(), False)
        self.assertEqual(response.context['password_change_form'].is_bound, False)
        new_update_info_form = response.context['update_info_form']
        self.assertIn('password_mismatch', new_update_info_form.error_messages)
        self.assertIn('email', new_update_info_form.errors)

    def test_UserjuliaPOSTUpdateUserInfoEmailKO(self):
        username = "julia"
        user = self.login(username)
        initial_data = {
            'first_name': user.user.first_name,
            'last_name': user.user.last_name,
            'email': "wrongEmailSyntax",
        }
        update_info_form = get_update_form(user.user, data=initial_data)
        update_info_form.is_valid()
        self.assertEqual(update_info_form.is_valid(), False)
        data = update_info_form.cleaned_data
        data.update({
            'update_info_form_submitted': 'yes',
            'email': "wrongEmailSyntax",
        })
        response = self.client.post(reverse("account_settings"), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "petition/account_settings.html")
        self.assertTemplateUsed(response, "layouts/base.html")
        self.assertEqual(response.context['user'], user)
        self.assertEqual(response.context['update_info_form_submitted'], True)
        self.assertEqual(response.context['delete_account_form_submitted'], False)
        self.assertEqual(response.context['password_change_form_submitted'], False)
        self.assertEqual(response.context['update_info_form'].is_valid(), False)
        self.assertEqual(response.context['update_info_form'].is_bound, True)
        self.assertEqual(response.context['delete_account_form'].is_valid(), False)
        self.assertEqual(response.context['delete_account_form'].is_bound, False)
        self.assertEqual(response.context['password_change_form'].is_valid(), False)
        self.assertEqual(response.context['password_change_form'].is_bound, False)
        new_update_info_form = response.context['update_info_form']
        self.assertIn('password_mismatch', new_update_info_form.error_messages)
        self.assertIn('email', new_update_info_form.errors)

    def test_UsermaxPOSTPassChangeKOWrongOldPass(self):
        username ="max"
        user = self.login(username)
        new_pass = 'eytksjezu375&#'
        data = {
            'password_change_form_submitted': 'yes',
            'old_password': 'WrongOldPass',
            'new_password1': new_pass,
            'new_password2': new_pass,
        }
        response = self.client.post(reverse("account_settings"), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "petition/account_settings.html")
        self.assertTemplateUsed(response, "layouts/base.html")
        self.assertEqual(response.context['user'], user)
        self.assertEqual(response.context['update_info_form_submitted'], False)
        self.assertEqual(response.context['delete_account_form_submitted'], False)
        self.assertEqual(response.context['password_change_form_submitted'], True)
        self.assertEqual(response.context['update_info_form'].is_valid(), True)
        self.assertEqual(response.context['update_info_form'].is_bound, True)
        self.assertEqual(response.context['delete_account_form'].is_valid(), False)
        self.assertEqual(response.context['delete_account_form'].is_bound, False)
        self.assertEqual(response.context['password_change_form'].is_valid(), False)
        self.assertEqual(response.context['password_change_form'].is_bound, True)
        self.logout()
        self.login(username)
        response2 = self.client.get(reverse("user_dashboard"))
        self.assertEqual(response2.status_code, 200)
        self.logout()
        self.login(username, password=new_pass)
        response3 = self.client.get(reverse("user_dashboard"), follow=True)
        self.assertRedirects(response3, reverse("login")+"?next="+reverse("user_dashboard"))

    def test_OneUserAdminCannotLeave(self):
        julia = self.login("julia")

        response = self.client.get(reverse("account_settings"))
        self.assertEquals(response.status_code, 200)
        orgs = response.context['orgs']
        for org in orgs:
            if org.is_last_admin(julia):
                self.assertEquals(org.leave, False)
            if org.members.count() == 1 and julia in org.members.all():
                self.assertEquals(org.leave, False)