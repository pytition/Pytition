from django.forms import ModelForm
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import UserCreationForm, UsernameField
from django.contrib.auth import get_user_model

from .models import Signature, PetitionTemplate, Petition
from .widgets import SwitchField

import uuid
from tinymce.widgets import TinyMCE


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


class PetitionTemplateForm(ModelForm):
    class Meta:
        model = PetitionTemplate
        #fields = ['side_text', 'target', 'linear_gradient_direction', 'gradient_from', 'gradient_to', 'bgcolor',
        #          'footer_text', 'footer_links', 'twitter_description', 'twitter_image', 'has_newsletter']
        fields = '__all__'
        help_texts = {
            'linear_gradient_direction': _(
                'This is a gradient color. If selected, the background color will be a gradient color. If not, the background color will be a monochrome background color.'),
            'gradient_to': _('Only used if gradient is selected'),
            'gradient_from': _('Only used if gradient is selected'),
            'footer_links': _(
                'Put a bullet point list of links, it will appear horizontally in the page footer'),
            'twitter_description': _(
                'This is the description of the petition, it will be displayed in Twitter/Facebook cards when the link is posted to social networks. To be tested via https://cards-dev.twitter.com/validator and https://developers.facebook.com/tools/debug/'),
            'twitter_image': _(
                'Picture displayed in Twitter/Facebook cards when the link is posted to social networks. To be tested via https://cards-dev.twitter.com/validator and https://developers.facebook.com/tools/debug/'),
            'has_newsletter': _(
                'Allow to chose whether the newsletter subscription checkbox is shown or not'),
            'newsletter_subscribe_http_data': _("""Only in case subscription to the newsletter via HTTP POST or GET methods. Put here data to be sent, using Python dictionary syntax. e.g.: <br>
                            {\'_wpcf7\': 21,<br>
                            \'_wpcf7_version\': \'4.9\',<br>
                            \'_wpcf7_locale\': \'fr_FR\',<br>
                            \'_wpcf7_unit_tag\': \'wpcf7-f21-p5398-o1\',<br>
                            \'_wpcf7_container_post': \'5398\',<br>
                            \'your-email\': \'\'<br>
                            }"""),
            'newsletter_subscribe_http_mailfield': _(
                'Only when HTTP POST or GET subscription method is used. Name of the field to send via GET or POST, containing the email address to subscribe. Following the example of preceding form field, that would be \'your-email\''),
            'newsletter_subscribe_http_url': _(
                'Only when HTTP POST or GET subscription method is used. Adresse HTTP à requêter via GET ou POST pour enregistrer quelqu\'un sur la newsletter'),
            'newsletter_subscribe_mail_subject': _(
                'Only when EMAIL subscription method is used. Inscrire ici la syntaxe de sujet du mail qui permet d\'inscrire quelqu\'un à la newsletter. Indiquez {} à la place où le mail du signataire doit être inséré. Ex: \'ADD NOM_LISTE {} NOM_SIGNATAIRE\''),
            'newsletter_subscribe_mail_from': _(
                'Only when EMAIL subscription method is used. L\'expéditeur du mail qui permet d\'enregistrer quelqu\'un à la newsletter. Il s\'agit généralement d\'une adresse qui est administratrice de la liste SYMPA ou MAILMAN'),
            'newsletter_subscribe_mail_to': _(
                'Only when EMAIL subscription method is used. Adresse email d\'administration de la liste, ex : sympa@NOM_LISTE.listes.vox.coop'),
            'newsletter_subscribe_method': _(
                'This selects the newsletter subscription method. It is either HTTP GET or POST or via sending EMAIL to the newsletter admin address'),
            'published': _(
                'If checked, the petition is published and accessible on the website by everybody. If not checked, the petition is only accessible by logged in users, others will get a 404 error.'),
            'newsletter_text': _('E.g.: I want to receive updates or informations from this organization.'),
            'sign_form_footer': _(
                'E.g.: Your data will stay strictly confidential and will not be sold, given away or exchanged with third parties. Informations about this campaign as well as other news about this organization will be sent to you if you checked the checkbox. You can unsubscribe at any moment.'),
            'org_twitter_handle': _(
                'The twitter account handle of the organization, starting with the \'@\' symbol. E.g.: @RAP_Asso. This is necessary in order to attribute the \'Twitter Card\' to the correct account. See https://developer.twitter.com/en/docs/tweets/optimize-with-cards/overview/summary'),
            'confirmation_email_sender': _('e.g.: petition@mydomain.tld'),
            'confirmation_email_smtp_host': _(
                'If you don\'t have a real email account, leave \'localhost\'.'),
            'confirmation_email_smtp_port': _(
                '25 for cleartext connection, 587 for STARTTLS, 465 for TLS. Prefer TLS if the email server supports it.'),
            'confirmation_email_smtp_user': _('Leave empty if you don\'t use any account autentication.'),
            'confirmation_email_smtp_password': _(
                'Leave empty if you don\'t use any account autentication.'),
            'confirmation_email_smtp_tls': _(
                'Connexion SMTP chiffrée via TLS, préférez ce réglage à STARTTLS. Ne pas cocher les 2. Les 2 réglages sont mutuellement exclusifs.'),
            'confirmation_email_smtp_starttls': _(
                'Connexion SMTP chiffrée via STARTTLS, préférez TLS à ce réglage. Ne pas cocher les 2. Les 2 réglages sont mutuellement exclusifs.'),
            'newsletter_subscribe_mail_smtp_host': _(
                'If you don\'t have a real email account, leave \'localhost\'.'),
            'newsletter_subscribe_mail_smtp_port': _(
                '25 for cleartext connection, 587 for STARTTLS, 465 for TLS. Prefer TLS if the email server supports it.'),
            'newsletter_subscribe_mail_smtp_user': _(
                'Leave empty if you don\'t use any account autentication.'),
            'newsletter_subscribe_mail_smtp_password': _(
                'Leave empty if you don\'t use any account autentication.'),
            'newsletter_subscribe_mail_smtp_tls': _(
                'SMTP connection encrypted via TLS, prefer this rather than STARTTLS if possible. Don\'t check both. The 2 settings are mutually exclusive.'),
            'newsletter_subscribe_mail_smtp_starttls': _(
                'Connexion SMTP chiffrée via STARTTLS, préférez TLS à ce réglage. Ne pas cocher les 2. Les 2 réglages sont mutuellement exclusifs.'),
        }
        labels = {
            'title': _('Petition title'),
            'text': _('Petition text'),
            'background': _('Background image (non-working)'),
            'mobile_background': _('Mobile phone background image (non-working)'),
            'top_picture': _('Top of text picture (non-working)'),
            'side_text': _('Side text, on top of form'),
            'target': _('Signature target number'),
            'linear_gradient_direction': _('Direction of linear gradient for background color'),
            'gradient_from': _('Source color for linear gradient'),
            'gradient_to': _('Destinatoin color for linear gradient'),
            'bgcolor': _('Color for monochrome background color'),
            'footer_text': _('Footer text'),
            'footer_links': _('Footer links'),
            'twitter_description': _('Description for Twitter/Facebook cards'),
            'twitter_image': _('Picture for Twitter/Facebook cards'),
            'has_newsletter': _('Is the petition associated with a newsletter?'),
            'newsletter_subscribe_http_data': _(
                'Data structure to be sent in order to subscribe someone to the newsletter in case of HTTP method'),
            'newsletter_subscribe_http_mailfield': _(
                'Name of the field which should contain the email value in the PHP data structure'),
            'newsletter_subscribe_http_url': _('HTTP URL for newsletter subscription'),
            'newsletter_subscribe_mail_subject': _('Email subject for newsletter subscription command'),
            'newsletter_subscribe_mail_from': _('FROM field for newsletter subscription command'),
            'newsletter_subscribe_mail_to': _('TO field for newsletter subscription command'),
            'newsletter_subscribe_method': _('Newsletter subscription method'),
            'published': _('Puslibhed'),
            'newsletter_text': _('Form label text of newsletter subscription checkbox'),
            'sign_form_footer': _('Sign form footer text'),
            'org_twitter_handle': _('Organization Twitter handle'),
            'confirmation_email_sender': _('Confirmation email sender address'),
            'confirmation_email_smtp_host': _('SMTP server hostname'),
            'confirmation_email_smtp_port': _('SMTP port'),
            'confirmation_email_smtp_user': _('SMTP username'),
            'confirmation_email_smtp_password': _('SMTP password'),
            'confirmation_email_smtp_tls': _('SMTP via TLS?'),
            'confirmation_email_smtp_starttls': _('SMTP via STARTTLS?'),
            'newsletter_subscribe_mail_smtp_host': _('SMTP server hostname'),
            'newsletter_subscribe_mail_smtp_port': _('SMTP port'),
            'newsletter_subscribe_mail_smtp_user': _('SMTP username'),
            'newsletter_subscribe_mail_smtp_password': _('SMTP password'),
            'newsletter_subscribe_mail_smtp_tls': _('SMTP via TLS?'),
            'newsletter_subscribe_mail_smtp_starttls': _('SMTP via STARTTLS?'),
        }


class PetitionCreationStep1(forms.Form):
    ### Ask for title ###
    title = forms.CharField(max_length=200)

class PetitionCreationStep2(forms.Form):
    ### Ask for content ###
    message = forms.CharField(widget=TinyMCE)

class PetitionCreationStep3(forms.Form):
    ### Ask for publication ###
    publish = forms.BooleanField(required=False, label=_("Publish the petition now?"))
    configure = forms.BooleanField(required=False, label=_("Save & Configure"))

class ContentForm(forms.Form):
    ### Content of a Petition ###
    title = forms.CharField(max_length=200)
    text = forms.CharField(widget=TinyMCE)
    side_text = forms.CharField(widget=TinyMCE, required=False)
    footer_text = forms.CharField(widget=TinyMCE, required=False)
    footer_links = forms.CharField(widget=TinyMCE, required=False)
    sign_form_footer = forms.CharField(required=False)


class EmailForm(forms.Form):
    ### E-mail settings of Petition ###
    use_custom_email_settings = SwitchField(required=False, label=_("Use custom e-mail settings?"))
    confirmation_email_sender = forms.EmailField(max_length=100, required=False)
    confirmation_email_smtp_host = forms.CharField(max_length=100, required=False)
    confirmation_email_smtp_port = forms.IntegerField(required=False)
    confirmation_email_smtp_user = forms.CharField(max_length=200, required=False)
    confirmation_email_smtp_password = forms.CharField(max_length=200, required=False)
    confirmation_email_smtp_tls = SwitchField(required=False, label=_("Use TLS?"))
    confirmation_email_smtp_starttls = SwitchField(required=False, label=_("Use STARTTLS?"))

    confirmation_email_smtp_port.widget.attrs.update({'min': 1, 'max': 65535})

    def clean(self):
        cleaned_data = super(EmailForm, self).clean()
        data = {}
        for field in self.base_fields:
            data[field] = cleaned_data.get(field)
        # FIXME: WIP

class SocialNetworkForm(forms.Form):
    ### Social Network settings of Petition ###
    twitter_description = forms.CharField(max_length=200, required=False)
    twitter_image = forms.CharField(max_length=500, required=False)
    org_twitter_handle = forms.CharField(max_length=20, required=False)

class NewsletterForm(forms.Form):
    ### Newsletter settings of Petition ###
    has_newsletter = SwitchField(required=False, label=_("Does this petition have a newsletter?"))
    newsletter_subscribe_http_data = forms.CharField(required=False)
    newsletter_subscribe_http_mailfield = forms.CharField(max_length=100,required=False)
    newsletter_subscribe_http_url = forms.CharField(max_length=1000, required=False)
    newsletter_subscribe_mail_subject = forms.CharField(max_length=1000, required=False)
    newsletter_subscribe_mail_from = forms.EmailField(required=False)
    newsletter_subscribe_mail_to = forms.EmailField(required=False)
    newsletter_subscribe_method = forms.ChoiceField(choices=Petition.NEWSLETTER_SUBSCRIBE_METHOD_CHOICES, required=False)
    newsletter_subscribe_mail_smtp_host = forms.CharField(max_length=100, required=False)
    newsletter_subscribe_mail_smtp_port = forms.IntegerField(required=False)
    newsletter_subscribe_mail_smtp_user = forms.CharField(max_length=200, required=False)
    newsletter_subscribe_mail_smtp_password = forms.CharField(max_length=200, required=False)
    newsletter_subscribe_mail_smtp_tls = SwitchField(required=False, label=_("Use TLS?"))
    newsletter_subscribe_mail_smtp_starttls = SwitchField(required=False, label=_("Use STARTTLS?"))

    newsletter_subscribe_mail_smtp_port.widget.attrs.update({'min': 1, 'max': 65535})

class PytitionUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ("username", "first_name", "last_name", "email")
        field_classes = {'username': UsernameField}

    def __init__(self, *args, **kwargs):
        super(PytitionUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['email'].required = True
