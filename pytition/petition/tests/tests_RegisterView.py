from django.test import TestCase
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from django.conf import settings
from django.contrib.auth import authenticate

from petition.models import PytitionUser

class PytitionUserRegister(TestCase):
    def setUp(self):
        pass

    def test_createPytitionUser(self):
        if settings.ALLOW_REGISTER:
            print("on allow register")
            response = self.client.get(reverse("register"))
            self.assertEqual(response.status_code, 200)

            data = {
                "username": "tototutu",
                "first_name": "Toto",
                "last_name": "Tutu",
                "email": "toto.tutu@mytotodomain.org",
                "password1": "mf6RJMqFvbE9Vq6g",
                "password2": "mf6RJMqFvbE9Vq6g",
                "answer": "",
                "email_confirm": "",
            }

            # No answer to Captcha
            response = self.client.post(reverse("register"), data=data)
            self.assertEqual(response.status_code, 200)
            form = response.context['form']
            self.assertEqual(form.is_bound, True)
            self.assertEqual(form.is_valid(), False)
            self.assertGreater(len(form.errors["answer"]), 0)
            self.assertEqual(len(form.errors), 1)
            self.assertNotIn("username", form.errors)
            self.assertNotIn("first_name", form.errors)
            self.assertNotIn("last_name", form.errors)
            self.assertNotIn("email", form.errors)
            self.assertNotIn("password1", form.errors)
            self.assertNotIn("password2", form.errors)
            self.assertNotIn("email_confirm", form.errors)
            pu = authenticate(username=data['username'], password=data['password1'])
            self.assertEqual(pu, None)
            with self.assertRaises(PytitionUser.DoesNotExist):
                toto = PytitionUser.objects.get(user__username=data['username'])

            # Wrong answer to Captcha
            response = self.client.get(reverse("register"))
            self.assertEqual(response.status_code, 200)
            answer = int(self.client.session["answer"])
            answer = answer + 1 # compute a wrong answer by adding 1 to correct answer
            data["answer"] = answer
            response = self.client.post(reverse("register"), data=data)
            self.assertEqual(response.status_code, 200)
            form = response.context['form']
            self.assertEqual(form.is_bound, True)
            self.assertEqual(form.is_valid(), False)
            self.assertGreater(len(form.errors["answer"]), 0)
            self.assertEqual(len(form.errors), 1)
            self.assertNotIn("username", form.errors)
            self.assertNotIn("first_name", form.errors)
            self.assertNotIn("last_name", form.errors)
            self.assertNotIn("email", form.errors)
            self.assertNotIn("password1", form.errors)
            self.assertNotIn("password2", form.errors)
            self.assertNotIn("email_confirm", form.errors)
            pu = authenticate(username=data['username'], password=data['password1'])
            self.assertEqual(pu, None)
            with self.assertRaises(PytitionUser.DoesNotExist):
                toto = PytitionUser.objects.get(user__username=data['username'])

            # Incorrect email
            response = self.client.get(reverse("register"))
            self.assertEqual(response.status_code, 200)
            answer = int(self.client.session["answer"])
            data2 = dict(data) # copy
            data2["answer"] = answer # correct answer
            data2["email"] = "invalid-email-syntax" # invalid email
            response = self.client.post(reverse("register"), data=data2)
            self.assertEqual(response.status_code, 200)
            form = response.context['form']
            self.assertEqual(form.is_bound, True)
            self.assertEqual(form.is_valid(), False)
            self.assertEqual(len(form.errors), 1)
            self.assertNotIn("answer", form.errors)
            self.assertNotIn("username", form.errors)
            self.assertNotIn("first_name", form.errors)
            self.assertNotIn("last_name", form.errors)
            self.assertIn("email", form.errors)
            self.assertNotIn("password1", form.errors)
            self.assertNotIn("password2", form.errors)
            self.assertNotIn("email_confirm", form.errors)
            pu = authenticate(username=data2['username'], password=data2['password1'])
            self.assertEqual(pu, None)
            with self.assertRaises(PytitionUser.DoesNotExist):
                toto = PytitionUser.objects.get(user__username=data2['username'])

            # Password mismatch (password1 != password2)
            response = self.client.get(reverse("register"))
            self.assertEqual(response.status_code, 200)
            answer = int(self.client.session["answer"])
            data2 = dict(data)
            data2["answer"] = answer # correct answer
            data2["password2"] = "not like password1" # invalid password
            response = self.client.post(reverse("register"), data=data2)
            self.assertEqual(response.status_code, 200)
            form = response.context['form']
            self.assertEqual(form.is_bound, True)
            self.assertEqual(form.is_valid(), False)
            self.assertEqual(len(form.errors), 1)
            self.assertNotIn("answer", form.errors)
            self.assertNotIn("username", form.errors)
            self.assertNotIn("first_name", form.errors)
            self.assertNotIn("last_name", form.errors)
            self.assertNotIn("email", form.errors)
            self.assertNotIn("password1", form.errors)
            self.assertIn("password2", form.errors)
            self.assertNotIn("email_confirm", form.errors)
            pu = authenticate(username=data2['username'], password=data2['password1'])
            self.assertEqual(pu, None)
            with self.assertRaises(PytitionUser.DoesNotExist):
                toto = PytitionUser.objects.get(user__username=data2['username'])

            # email_confirm filled-up
            response = self.client.get(reverse("register"))
            self.assertEqual(response.status_code, 200)
            answer = int(self.client.session["answer"])
            data2 = dict(data) # copy
            data2["answer"] = answer # correct answer
            data2["email_confirm"] = data2["email"]
            response = self.client.post(reverse("register"), data=data2)
            self.assertEqual(response.status_code, 200)
            form = response.context['form']
            self.assertEqual(form.is_bound, True)
            self.assertEqual(form.is_valid(), False)
            self.assertEqual(len(form.errors), 1)
            self.assertNotIn("answer", form.errors)
            self.assertNotIn("username", form.errors)
            self.assertNotIn("first_name", form.errors)
            self.assertNotIn("last_name", form.errors)
            self.assertNotIn("email", form.errors)
            self.assertNotIn("password1", form.errors)
            self.assertNotIn("password2", form.errors)
            self.assertIn("email_confirm", form.errors)
            pu = authenticate(username=data2['username'], password=data2['password1'])
            self.assertEqual(pu, None)
            with self.assertRaises(PytitionUser.DoesNotExist):
                toto = PytitionUser.objects.get(user__username=data2['username'])

            # Check what happens if mandatory fields are blank
            data2 = dict()
            response = self.client.post(reverse("register"), data=data2)
            self.assertEqual(response.status_code, 200)
            form = response.context['form']
            self.assertEqual(form.is_bound, True)
            self.assertEqual(form.is_valid(), False)
            self.assertEqual(len(form.errors), 6)

            # Everything is correct
            response = self.client.get(reverse("register"))
            self.assertEqual(response.status_code, 200)
            answer = int(self.client.session["answer"])
            data["answer"] = answer
            response = self.client.post(reverse("register"), data=data)
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, reverse("login"))
            toto = PytitionUser.objects.get(user__username=data['username'])
            self.assertEqual(toto.user.email, data["email"])
            self.assertEqual(toto.user.first_name, data["first_name"])
            self.assertEqual(toto.user.last_name, data["last_name"])
            # Let's try to authenticate, to check password is OK
            pu = authenticate(username=data['username'], password=data['password1'])
            self.assertNotEqual(pu, None)
        else:
            with self.assertRaises(NoReverseMatch):
                response = self.client.get(reverse("register"))