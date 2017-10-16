from django.db import models
from django.utils.html import mark_safe, strip_tags
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings

from tinymce import models as tinymce_models
from colorfield.fields import ColorField

import requests


class Petition(models.Model):

    NO =           "no gradient"
    RIGHT =        "to right"
    BOTTOM =       "to bottom"
    BOTTOM_RIGHT = "to bottom right"
    BOTTOM_LEFT =  "to bottom left"

    LINEAR_GRADIENT_CHOICES = (
        (NO,           "no gradient"),
        (RIGHT,        "to right"),
        (BOTTOM,       "to bottom"),
        (BOTTOM_RIGHT, "to bottom right"),
        (BOTTOM_LEFT,  "to bottom left")
    )

    title = tinymce_models.HTMLField()
    text = tinymce_models.HTMLField()
    background = models.ImageField(blank=True)
    mobile_background = models.ImageField(blank=True)
    top_picture = models.ImageField(blank=True)
    side_text = tinymce_models.HTMLField(blank=True)
    target = models.IntegerField(default=500)
    linear_gradient_direction = models.CharField(choices=LINEAR_GRADIENT_CHOICES, max_length=15, default=NO, blank=True)
    gradient_from = ColorField(blank=True)
    gradient_to = ColorField(blank=True)
    bgcolor = ColorField(blank=True)
    footer_text = tinymce_models.HTMLField(default="Cette pétition est hébergée sur le site de RAP.")
    footer_links = tinymce_models.HTMLField(blank=True)
    twitter_description = models.CharField(max_length=200, blank=True)
    twitter_image = models.CharField(max_length=500, blank=True)

    def sign(self, firstname, lastname, email, phone, confirmation_hash, url, subscribe):
        signature = Signature.objects.create(first_name=firstname, last_name=lastname, email=email, phone=phone,
                                             petition_id=self.pk, confirmation_hash=confirmation_hash)
        html_message = render_to_string("petition/confirmation_email.html", {'firstname': firstname, 'url': url})
        message = strip_tags(html_message)
        send_mail("Confirmez votre signature à notre pétition", message, "petition@antipub.org", [email],
                  fail_silently=False, html_message=html_message)
        if subscribe:
            data = settings.NEWSLETTER_SUBSCRIBE_DATA
            data[settings.NEWSLETTER_SUBSCRIBE_EMAIL_FIELDNAME] = email
            if settings.NEWSLETTER_SUBSCRIBE_METHOD == "POST":
                requests.post(settings.NEWSLETTER_SUBSCRIBE_URL, data)
            elif settings.NEWSLETTER_SUBSCRIBE_METHOD == "GET":
                requests.get(settings.NEWSLETTER_SUBSCRIBE_URL, data)
            else:
                raise ValueError("setting NEWSLETTER_SUBSCRIBE_METHOD must either be POST or GET")

    def __str__(self):
        return mark_safe(self.title)

    def __repr__(self):
        return mark_safe(self.title)


class Signature(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    confirmation_hash = models.CharField(max_length=128)
    confirmed = models.BooleanField(default=False)
    petition = models.ForeignKey(Petition, on_delete=models.CASCADE)

    def __str__(self):
        return "[{}:{}] {} {}".format(self.petition.id, "OK" if self.confirmed else "..", self.first_name,
                                      self.last_name)

    def __repr__(self):
        return "[{}:{}] {} {}".format(self.petition.id, "OK" if self.confirmed else "..", self.first_name,
                                      self.last_name)
