from django.db import models
from django.utils.html import mark_safe, strip_tags

from tinymce import models as tinymce_models
from colorfield.fields import ColorField

import html


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

    MAIL = "MAIL"
    POST = "POST"
    GET = "GET"

    NEWSLETTER_SUBSCRIBE_METHOD_CHOICES = (
        (MAIL, "MAIL"),
        (POST, "POST"),
        (GET,  "GET")
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
    has_newsletter = models.BooleanField(default=False)
    newsletter_subscribe_http_data = models.TextField(blank=True)
    newsletter_subscribe_http_mailfield = models.CharField(max_length=100, blank=True)
    newsletter_subscribe_http_url = models.CharField(max_length=1000, blank=True)
    newsletter_subscribe_mail_subject = models.CharField(max_length=1000, blank=True)
    newsletter_subscribe_mail_from = models.CharField(max_length=500, blank=True)
    newsletter_subscribe_mail_to = models.CharField(max_length=500, blank=True)
    newsletter_subscribe_method = models.CharField(choices=NEWSLETTER_SUBSCRIBE_METHOD_CHOICES, max_length=4,
                                                   default=MAIL)
    published = models.BooleanField(default=False)
    newsletter_text = models.CharField(max_length=1000, blank=True)

    @property
    def raw_twitter_description(self):
        return html.unescape(mark_safe(strip_tags(self.twitter_description)))

    @property
    def raw_text(self):
        return html.unescape(mark_safe(strip_tags(self.text)))

    @property
    def raw_title(self):
        return html.unescape(mark_safe(strip_tags(self.title)))

    def __str__(self):
        return self.raw_title

    def __repr__(self):
        return self.raw_title


class Signature(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField()
    confirmation_hash = models.CharField(max_length=128)
    confirmed = models.BooleanField(default=False)
    petition = models.ForeignKey(Petition, on_delete=models.CASCADE)
    subscribed_to_mailinglist = models.BooleanField(default=False)
    date = models.DateTimeField(blank=True, auto_now_add=True)

    def __str__(self):
        return html.unescape("[{}:{}] {} {}".format(self.petition.id, "OK" if self.confirmed else "..", self.first_name,
                                                    self.last_name))

    def __repr__(self):
        return html.unescape("[{}:{}] {} {}".format(self.petition.id, "OK" if self.confirmed else "..", self.first_name,
                                      self.last_name))
