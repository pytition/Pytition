from django.forms import ModelForm
from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import Signature

import uuid


class SignatureForm(ModelForm):

    class Meta:
        model = Signature
        fields = ['first_name', 'last_name', 'phone', 'email', 'subscribed_to_mailinglist']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': _('First name *'), 'class': 'form-control has-feedback eaFullWidthContent'}),
            'last_name': forms.TextInput(attrs={'placeholder': _('Last name *'), 'class': 'form-control has-feedback eaFullWidthContent'}),
            'phone': forms.TextInput(attrs={'placeholder': _('Phone number'), 'class': 'form-control has-feedback eaFullWidthContent'}),
            'email': forms.EmailInput(attrs={'placeholder': _('Email address *'), 'class': 'form-control has-feedback eaFullWidthContent'})
        }

        labels = { f : '' for f in  ['first_name', 'last_name', 'phone', 'email'] }

    def __init__(self, petition=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.petition = petition
        if not petition.has_newsletter:
            del self.fields['subscribed_to_mailinglist']
        else:
            self.fields['subscribed_to_mailinglist'].label = self.instance.petition.newsletter_text

    def save(self, commit=True):
        object = super().save(commit=False)
        hashstring = str(uuid.uuid4())
        object.confirmation_hash = hashstring
        object.confirmed = False
        if commit:
            object.save()
        return object