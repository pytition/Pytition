from django.forms import ModelForm, ValidationError
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import UserCreationForm, UsernameField
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.utils.html import mark_safe, strip_tags

from .models import Signature, PetitionTemplate, Petition, Organization, PytitionUser, SlugModel
from .widgets import SwitchField

import uuid
import html
from tinymce.widgets import TinyMCE
from colorfield.fields import ColorWidget


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


class PetitionCreationStep1(forms.Form):
    ### Ask for title ###
    title = forms.CharField(max_length=200)

    def clean_title(self):
        title = self.cleaned_data.get('title')
        #slugtext = slugify(html.unescape(mark_safe(strip_tags(title).strip())))
        filters = {'title': title}
        if self.owned_by_org:
            org = Organization.objects.get(slugname=self.orgslugname)
            filters.update({'org': org})
        else:
            user = PytitionUser.objects.get(user__username=self.username)
            filters.update({'user': user})
        results = Petition.objects.filter(**filters)
        if results.count() > 0:
            self.add_error('title', ValidationError(_("There is already a petition with this title"), code="invalid"))

        return title

    def __init__(self, *args, **kwargs):
        if "orgslugname" in kwargs:
            self.orgslugname = kwargs.pop("orgslugname")
            self.owned_by_org = True
        elif "user_name" in kwargs:
            self.owned_by_org = False
            self.username = kwargs.pop("user_name")
        else:
            raise ValueError(_("You should either provide an org name or a user name"))
        super(PetitionCreationStep1, self).__init__(*args, **kwargs)


class PetitionCreationStep2(forms.Form):
    ### Ask for content ###
    message = forms.CharField(widget=TinyMCE)


class PetitionCreationStep3(forms.Form):
    ### Ask for publication ###
    publish = forms.BooleanField(required=False, label=_("Publish the petition now?"))
    configure = forms.BooleanField(required=False, label=_("Save & Configure"))


class ContentFormGeneric(forms.Form):
    ### Content of a Petition ###
    text = forms.CharField(widget=TinyMCE)
    target = forms.IntegerField(required=False)
    side_text = forms.CharField(widget=TinyMCE, required=False)
    footer_text = forms.CharField(widget=TinyMCE, required=False)
    footer_links = forms.CharField(widget=TinyMCE, required=False)
    sign_form_footer = forms.CharField(required=False)


class ContentFormPetition(ContentFormGeneric):
    title = forms.CharField(max_length=200)
    paper_signatures = forms.IntegerField()
    field_order = ('title', 'paper_signatures')


class ContentFormTemplate(ContentFormGeneric):
    name = forms.CharField(max_length=50)
    field_order = ('name', )


class EmailForm(forms.Form):
    ### E-mail settings of Petition ###
    confirmation_email_reply = forms.EmailField(max_length=100, required=False,
                                                label=_("Your contact email. It will be used as \"Reply-To\" field of"
                                                        " the confirmation email sent to signatories. People responding"
                                                        " to confirmation email will in fact respond to this address."))


# This form is not rendered like the others, it is just used to "parse" POSTed data
class SocialNetworkForm(forms.Form):
    ### Social Network settings of Petition ###
    twitter_description = forms.CharField(max_length=200, required=False)
    twitter_image = forms.FileField(max_length=500, required=False)
    org_twitter_handle = forms.CharField(max_length=20, required=False)
    remove_twitter_image = forms.BooleanField(required=False, initial=False)


class NewsletterForm(forms.Form):
    ### Newsletter settings of Petition ###
    has_newsletter = SwitchField(required=False, label=_("Does this petition have a newsletter?"))
    newsletter_text = forms.CharField(required=False)
    newsletter_subscribe_http_data = forms.CharField(max_length=1000, required=False)
    newsletter_subscribe_http_mailfield = forms.CharField(max_length=100,required=False)
    newsletter_subscribe_http_url = forms.CharField(max_length=1000, required=False)
    newsletter_subscribe_mail_subject = forms.CharField(max_length=1000, required=False)
    newsletter_subscribe_mail_from = forms.EmailField(required=False)
    newsletter_subscribe_mail_to = forms.EmailField(required=False)
    newsletter_subscribe_method = forms.ChoiceField(choices=Petition.NEWSLETTER_SUBSCRIBE_METHOD_CHOICES, required=False)
    newsletter_subscribe_mail_smtp_host = forms.CharField(max_length=100, required=False)
    newsletter_subscribe_mail_smtp_port = forms.IntegerField(required=False)
    newsletter_subscribe_mail_smtp_user = forms.CharField(max_length=200, required=False)
    newsletter_subscribe_mail_smtp_password = forms.CharField(max_length=200, required=False,
                                                              widget=forms.PasswordInput())
    newsletter_subscribe_mail_smtp_tls = SwitchField(required=False, label=_("Use TLS?"))
    newsletter_subscribe_mail_smtp_starttls = SwitchField(required=False, label=_("Use STARTTLS?"))

    newsletter_subscribe_mail_smtp_port.widget.attrs.update({'min': 1, 'max': 65535})

    def clean(self):
        # FIXME: WIP
        cleaned_data = super(NewsletterForm, self).clean()
        data = {}
        for field in self.base_fields:
            data[field] = cleaned_data.get(field)

        if data['newsletter_subscribe_mail_smtp_tls'] and data['newsletter_subscribe_mail_smtp_starttls']:
            self.add_error('newsletter_subscribe_mail_smtp_tls', ValidationError(_("You cannot select both TLS and STARTTLS."), code="invalid"))

        if data['newsletter_subscribe_mail_smtp_port'] < 1 or data['newsletter_subscribe_mail_smtp_port'] > 65535:
            self.add_error('newsletter_subscribe_mail_smtp_port', ValidationError(_("SMTP port must be >= 1 and <= 65535"),
                                                                                  code="invalid"))

        return self.cleaned_data


class StyleForm(forms.Form):
    ### Graphical UI style info of Petition ###
    bgcolor = forms.CharField(widget=ColorWidget)
    linear_gradient_direction = forms.ChoiceField(choices=Petition.LINEAR_GRADIENT_CHOICES)
    gradient_from = forms.CharField(widget=ColorWidget)
    gradient_to = forms.CharField(widget=ColorWidget)


class PytitionUserCreationForm(UserCreationForm):
    answer = forms.IntegerField(required=True)
    email_confirm = forms.EmailField(widget=forms.HiddenInput, required=False)
    class Meta:
        model = get_user_model()
        fields = ("username", "first_name", "last_name", "email", "answer", "email_confirm")
        field_classes = {'username': UsernameField}

    def __init__(self, request=None, *args, **kwargs):
        super(PytitionUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['email'].required = True
        self.request = request

    def clean(self):
        session = self.request.session
        cleaned_data = super(UserCreationForm, self).clean()
        if "answer" in cleaned_data and int(cleaned_data["answer"]) != session['answer']:
            self.add_error("answer", ValidationError(_("Wrong answer"), code="invalid"))
        if "email_confirm" in cleaned_data and cleaned_data["email_confirm"] != "":
            # Normal users should end up with email_confirm == "" because the field is hidden
            # Robots might fill up this field, thus we throw an error
            self.add_error("email_confirm", ValidationError("Incorrect email confirmation", code="invalid"))
        if 'answer' in cleaned_data:
            del cleaned_data['answer']
        if 'answer' in self.data:
            # QueryDict() objects are immutable!
            newdata = dict(self.data.items())
            del newdata['answer']
            self.data = newdata
        self.cleaned_data = cleaned_data
        return cleaned_data


class UpdateInfoForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ("first_name", "last_name", "email")

    def __init__(self, user, *args, **kwargs):
        super(UpdateInfoForm, self).__init__(*args, **kwargs)
        self.user = user
        del self.fields['password1']
        del self.fields['password2']

    def save(self, commit=True):
        self.user.email = self.cleaned_data['email']
        self.user.first_name = self.cleaned_data['first_name']
        self.user.last_name = self.cleaned_data['last_name']
        if commit:
            self.user.save()
        return self.user


class DeleteAccountForm(forms.Form):
    validation = forms.CharField()

    def clean(self):
        cleaned_data = super(DeleteAccountForm, self).clean()
        valid = cleaned_data.get('validation')
        if valid != _("DROP MY ACCOUNT"):
            self.add_error('validation', ValidationError(_("You miss-typed the validation code"), code="invalid"))
        return self.cleaned_data


class OrgCreationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ('name', )

    def clean(self):
        cleaned_data = super(OrgCreationForm, self).clean()
        name = cleaned_data.get('name')
        if name in ['..', '.']:
            self.add_error('name',
                           ValidationError(_("This is an invalid Organization name. Please try something else."),
                                           code="invalid"))
        return self.cleaned_data
