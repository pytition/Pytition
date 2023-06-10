from django.contrib import admin
from django.forms import ModelForm
from django.utils.translation import gettext_lazy
from django.contrib import messages
from django.core.exceptions import ValidationError
from django import forms

from tinymce.widgets import TinyMCE

from .models import Signature, Petition, Organization, PytitionUser, PetitionTemplate, Permission, SlugModel
from .views import send_confirmation_email


@admin.register(PytitionUser)
class PytitionUserAdmin(admin.ModelAdmin):
    list_display = ('name', )

    def name(self, pu):
        return pu

    name.description = gettext_lazy("Name")


@admin.register(SlugModel)
class SlugModelAdmin(admin.ModelAdmin):
    pass


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'petition_num', 'user_num')

    def petition_num(self, org):
        return org.petition_set.count()

    def user_num(self, org):
        return org.members.count()

    petition_num.description = gettext_lazy('Number of petitions')
    user_num.description = gettext_lazy('Number of members')


def confirm(modeladmin, request, queryset):
    try:
        for signature in queryset:
            signature.confirm()
            signature.save()
    except ValidationError as e:
        messages.error(request, gettext_lazy("Error: {}").format(e.message))


def resend_confirmation_mail(modeladmin, request, queryset):
    for signature in queryset:
        send_confirmation_email(request, signature)


confirm.short_description = gettext_lazy("Confirm the signatures")
resend_confirmation_mail.short_description = gettext_lazy("Send the confirmation email once again")


@admin.register(Signature)
class SignatureAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone', 'email', 'confirmed', 'subscribed_to_mailinglist', 'petition', 'date')
    list_filter = ('petition', 'confirmed')
    actions = [confirm, resend_confirmation_mail]
    search_fields = ('first_name', 'last_name', 'phone', 'email')
    change_form_template = 'petition/signature_change_form.html'


#class SlugInlineAdmin(admin.TabularInline):
    #Petition.slugs.through


class PetitionAdminForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(PetitionAdminForm, self).__init__(*args, **kwargs)
        self.fields['user'].required = False
        self.fields['org'].required = False

    class Meta:
        model = Petition
        #inlines = (SlugInlineAdmin, )
        exclude = ('slugs', )
        help_texts = {
            'linear_gradient_direction': gettext_lazy('This is a gradient color. If selected, the background color will be a gradient color. If not, the background color will be a monochrome background color.'),
            'gradient_to': gettext_lazy('Only used if gradient is selected'),
            'gradient_from': gettext_lazy('Only used if gradient is selected'),
            'footer_links': gettext_lazy('Put a bullet point list of links, it will appear horizontally in the page footer'),
            'twitter_description': gettext_lazy('This is the description of the petition, it will be displayed in Twitter/Facebook cards when the link is posted to social networks. To be tested via https://cards-dev.twitter.com/validator and https://developers.facebook.com/tools/debug/'),
            'twitter_image': gettext_lazy('Picture displayed in Twitter/Facebook cards when the link is posted to social networks. To be tested via https://cards-dev.twitter.com/validator and https://developers.facebook.com/tools/debug/'),
            'has_newsletter': gettext_lazy('Allow to chose whether the newsletter subscription checkbox is shown or not'),
            'newsletter_subscribe_http_data': gettext_lazy("""Only in case subscription to the newsletter via HTTP POST or GET methods. Put here data to be sent, using Python dictionary syntax. e.g.: <br>
                    {\'_wpcf7\': 21,<br>
                    \'_wpcf7_version\': \'4.9\',<br>
                    \'_wpcf7_locale\': \'fr_FR\',<br>
                    \'_wpcf7_unit_tag\': \'wpcf7-f21-p5398-o1\',<br>
                    \'_wpcf7_container_post': \'5398\',<br>
                    \'your-email\': \'\'<br>
                    }"""),
            'newsletter_subscribe_http_mailfield': gettext_lazy('Only when HTTP POST or GET subscription method is used. Name of the field to send via GET or POST, containing the email address to subscribe. Following the example of preceding form field, that would be \'your-email\''),
            'newsletter_subscribe_http_url': gettext_lazy('Only when HTTP POST or GET subscription method is used. Adresse HTTP à requêter via GET ou POST pour enregistrer quelqu\'un sur la newsletter'),
            'newsletter_subscribe_mail_subject': gettext_lazy('Only when EMAIL subscription method is used. Inscrire ici la syntaxe de sujet du mail qui permet d\'inscrire quelqu\'un à la newsletter. Indiquez {} à la place où le mail du signataire doit être inséré. Ex: \'ADD NOM_LISTE {} NOM_SIGNATAIRE\''),
            'newsletter_subscribe_mail_from': gettext_lazy('Only when EMAIL subscription method is used. L\'expéditeur du mail qui permet d\'enregistrer quelqu\'un à la newsletter. Il s\'agit généralement d\'une adresse qui est administratrice de la liste SYMPA ou MAILMAN'),
            'newsletter_subscribe_mail_to': gettext_lazy('Only when EMAIL subscription method is used. Adresse email d\'administration de la liste, ex : sympa@NOM_LISTE.listes.vox.coop'),
            'newsletter_subscribe_method': gettext_lazy('This selects the newsletter subscription method. It is either HTTP GET or POST or via sending EMAIL to the newsletter admin address'),
            'published': gettext_lazy('If checked, the petition is published and accessible on the website by everybody. If not checked, the petition is only accessible by logged in users, others will get a 404 error.'),
            'newsletter_text': gettext_lazy('E.g.: I want to receive updates or informations from this organization.'),
            'sign_form_footer': gettext_lazy('E.g.: Your data will stay strictly confidential and will not be sold, given away or exchanged with third parties. Informations about this campaign as well as other news about this organization will be sent to you if you checked the checkbox. You can unsubscribe at any moment.'),
            'org_twitter_handle': gettext_lazy('The twitter account handle of the organization, starting with the \'@\' symbol. E.g.: @RAP_Asso. This is necessary in order to attribute the \'Twitter Card\' to the correct account. See https://developer.twitter.com/en/docs/tweets/optimize-with-cards/overview/summary'),
            'use_custom_email_settings': gettext_lazy('Check if you want to use your own E-Mail SMTP account.'),
            'confirmation_email_reply': gettext_lazy('e.g.: petition@mydomain.tld'),
            'newsletter_subscribe_mail_smtp_host': gettext_lazy('If you don\'t have a real email account, leave \'localhost\'.'),
            'newsletter_subscribe_mail_smtp_port': gettext_lazy('25 for cleartext connection, 587 for STARTTLS, 465 for TLS. Prefer TLS if the email server supports it.'),
            'newsletter_subscribe_mail_smtp_user': gettext_lazy('Leave empty if you don\'t use any account autentication.'),
            'newsletter_subscribe_mail_smtp_password': gettext_lazy('Leave empty if you don\'t use any account autentication.'),
            'newsletter_subscribe_mail_smtp_tls': gettext_lazy('SMTP connection encrypted via TLS, prefer this rather than STARTTLS if possible. Don\'t check both. The 2 settings are mutually exclusive.'),
            'newsletter_subscribe_mail_smtp_starttls': gettext_lazy('Connexion SMTP chiffrée via STARTTLS, préférez TLS à ce réglage. Ne pas cocher les 2. Les 2 réglages sont mutuellement exclusifs.'),
        }
        labels = {
            'title': gettext_lazy('Petition title'),
            'text': gettext_lazy('Petition text'),
            'side_text': gettext_lazy('Side text, on top of form'),
            'target': gettext_lazy('Signature target number'),
            'paper_signatures': gettext_lazy('Number of paper (or other external medium) signatures'),
            'paper_signatures_enabled': gettext_lazy('Enable paper signatures accounting'),
            'linear_gradient_direction': gettext_lazy('Direction of linear gradient for background color'),
            'gradient_from': gettext_lazy('Source color for linear gradient'),
            'gradient_to': gettext_lazy('Destinatoin color for linear gradient'),
            'bgcolor': gettext_lazy('Color for monochrome background color'),
            'footer_text': gettext_lazy('Footer text'),
            'footer_links': gettext_lazy('Footer links'),
            'twitter_description': gettext_lazy('Description for Twitter/Facebook cards'),
            'twitter_image': gettext_lazy('Picture for Twitter/Facebook cards'),
            'has_newsletter': gettext_lazy('Is the petition associated with a newsletter?'),
            'newsletter_subscribe_http_data': gettext_lazy('Data structure to be sent in order to subscribe someone to the newsletter in case of HTTP method'),
            'newsletter_subscribe_http_mailfield': gettext_lazy('Name of the field which should contain the email value in the PHP data structure'),
            'newsletter_subscribe_http_url': gettext_lazy('HTTP URL for newsletter subscription'),
            'newsletter_subscribe_mail_subject': gettext_lazy('Email subject for newsletter subscription command'),
            'newsletter_subscribe_mail_from': gettext_lazy('FROM field for newsletter subscription command'),
            'newsletter_subscribe_mail_to': gettext_lazy('TO field for newsletter subscription command'),
            'newsletter_subscribe_method': gettext_lazy('Newsletter subscription method'),
            'published': gettext_lazy('Puslibhed'),
            'newsletter_text': gettext_lazy('Form label text of newsletter subscription checkbox'),
            'sign_form_footer': gettext_lazy('Sign form footer text'),
            'org_twitter_handle': gettext_lazy('Organization Twitter handle'),
            'use_custom_email_settings': gettext_lazy('Use custom e-mail settings?'),
            'confirmation_email_reply': gettext_lazy('Confirmation email Reply-to address'),
            'newsletter_subscribe_mail_smtp_host': gettext_lazy('SMTP server hostname'),
            'newsletter_subscribe_mail_smtp_port': gettext_lazy('SMTP port'),
            'newsletter_subscribe_mail_smtp_user': gettext_lazy('SMTP username'),
            'newsletter_subscribe_mail_smtp_password': gettext_lazy('SMTP password'),
            'newsletter_subscribe_mail_smtp_tls': gettext_lazy('SMTP via TLS?'),
            'newsletter_subscribe_mail_smtp_starttls': gettext_lazy('SMTP via STARTTLS?'),
        }


@admin.register(Petition)
class PetitionAdmin(admin.ModelAdmin):
    change_form_template = 'petition/petition_change_form.html'
    form = PetitionAdminForm
    search_fields = ('title', )
    list_display = ('title', 'non_confirmed_signature_number', 'confirmed_signature_number')
    fieldsets = (
        (gettext_lazy('To whom is this petition?'),
         {
             'fields': ('org', 'user')
         }
         ),
        (gettext_lazy('Content of the petition'),
         {
          'fields': ('title', 'text', 'side_text', 'footer_text', 'footer_links', 'sign_form_footer', 'target',
                     'paper_signatures_enabled', 'paper_signatures')
         }
        ),
        (gettext_lazy('Background color'),
         {
             'fields': ('linear_gradient_direction', 'gradient_from', 'gradient_to', 'bgcolor')
         }
         ),
        (gettext_lazy('Setup of the newsletter associated to the petition'),
         {
             'fields': ('has_newsletter', 'newsletter_text', 'newsletter_subscribe_method',
                        'newsletter_subscribe_http_data', 'newsletter_subscribe_http_mailfield',
                        'newsletter_subscribe_http_url', 'newsletter_subscribe_mail_subject',
                        'newsletter_subscribe_mail_from', 'newsletter_subscribe_mail_to',
                        'newsletter_subscribe_mail_smtp_host', 'newsletter_subscribe_mail_smtp_port',
                        'newsletter_subscribe_mail_smtp_user', 'newsletter_subscribe_mail_smtp_password',
                        'newsletter_subscribe_mail_smtp_tls', 'newsletter_subscribe_mail_smtp_starttls')
         }
         ),
        (gettext_lazy('Confirmation email setup'),
         {
             'fields': ('confirmation_email_reply', )
         }
        ),
        (gettext_lazy('Petition meta-data for social networks'),
         {
             'fields': ('twitter_description', 'twitter_image', 'org_twitter_handle')
         }),
        (gettext_lazy('Publish the petition'),
         {
             'fields': ('published', )
         })
    )

    def non_confirmed_signature_number(self, petition):
        return petition.get_signature_number(confirmed=False)
    non_confirmed_signature_number.short_description = gettext_lazy('Unconfirmed signatures')

    def confirmed_signature_number(self, petition):
        return petition.get_signature_number(confirmed=True)
    confirmed_signature_number.short_description = gettext_lazy('Confirmed signatures')


class PetitionTemplateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(PetitionTemplateForm, self).__init__(*args, **kwargs)
        self.fields['user'].required = False
        self.fields['org'].required = False

    class Meta:
        model = PetitionTemplate
        fields = ['linear_gradient_direction', 'side_text']
        help_texts = {
            'linear_gradient_direction': gettext_lazy('This is a gradient color. If selected, the background color will be a gradient color. If not, the background color will be a monochrome background color.'),
            'gradient_to': gettext_lazy('Only used if gradient is selected'),
            'gradient_from': gettext_lazy('Only used if gradient is selected'),
            'footer_links': gettext_lazy('Put a bullet point list of links, it will appear horizontally in the page footer'),
            'twitter_description': gettext_lazy('This is the description of the petition, it will be displayed in Twitter/Facebook cards when the link is posted to social networks. To be tested via https://cards-dev.twitter.com/validator and https://developers.facebook.com/tools/debug/'),
            'twitter_image': gettext_lazy('Picture displayed in Twitter/Facebook cards when the link is posted to social networks. To be tested via https://cards-dev.twitter.com/validator and https://developers.facebook.com/tools/debug/'),
            'has_newsletter': gettext_lazy('Allow to chose whether the newsletter subscription checkbox is shown or not'),
            'newsletter_subscribe_http_data': gettext_lazy("""Only in case subscription to the newsletter via HTTP POST or GET methods. Put here data to be sent, using Python dictionary syntax. e.g.: <br>
                    {\'_wpcf7\': 21,<br>
                    \'_wpcf7_version\': \'4.9\',<br>
                    \'_wpcf7_locale\': \'fr_FR\',<br>
                    \'_wpcf7_unit_tag\': \'wpcf7-f21-p5398-o1\',<br>
                    \'_wpcf7_container_post': \'5398\',<br>
                    \'your-email\': \'\'<br>
                    }"""),
            'newsletter_subscribe_http_mailfield': gettext_lazy('Only when HTTP POST or GET subscription method is used. Name of the field to send via GET or POST, containing the email address to subscribe. Following the example of preceding form field, that would be \'your-email\''),
            'newsletter_subscribe_http_url': gettext_lazy('Only when HTTP POST or GET subscription method is used. Adresse HTTP à requêter via GET ou POST pour enregistrer quelqu\'un sur la newsletter'),
            'newsletter_subscribe_mail_subject': gettext_lazy('Only when EMAIL subscription method is used. Inscrire ici la syntaxe de sujet du mail qui permet d\'inscrire quelqu\'un à la newsletter. Indiquez {} à la place où le mail du signataire doit être inséré. Ex: \'ADD NOM_LISTE {} NOM_SIGNATAIRE\''),
            'newsletter_subscribe_mail_from': gettext_lazy('Only when EMAIL subscription method is used. L\'expéditeur du mail qui permet d\'enregistrer quelqu\'un à la newsletter. Il s\'agit généralement d\'une adresse qui est administratrice de la liste SYMPA ou MAILMAN'),
            'newsletter_subscribe_mail_to': gettext_lazy('Only when EMAIL subscription method is used. Adresse email d\'administration de la liste, ex : sympa@NOM_LISTE.listes.vox.coop'),
            'newsletter_subscribe_method': gettext_lazy('This selects the newsletter subscription method. It is either HTTP GET or POST or via sending EMAIL to the newsletter admin address'),
            'published': gettext_lazy('If checked, the petition is published and accessible on the website by everybody. If not checked, the petition is only accessible by logged in users, others will get a 404 error.'),
            'newsletter_text': gettext_lazy('E.g.: I want to receive updates or informations from this organization.'),
            'sign_form_footer': gettext_lazy('E.g.: Your data will stay strictly confidential and will not be sold, given away or exchanged with third parties. Informations about this campaign as well as other news about this organization will be sent to you if you checked the checkbox. You can unsubscribe at any moment.'),
            'org_twitter_handle': gettext_lazy('The twitter account handle of the organization, starting with the \'@\' symbol. E.g.: @RAP_Asso. This is necessary in order to attribute the \'Twitter Card\' to the correct account. See https://developer.twitter.com/en/docs/tweets/optimize-with-cards/overview/summary'),
            'use_custom_email_settings': gettext_lazy('Check if you want to use your own E-Mail SMTP account.'),
            'confirmation_email_reply': gettext_lazy('e.g.: petition@mydomain.tld'),
            'newsletter_subscribe_mail_smtp_host': gettext_lazy('If you don\'t have a real email account, leave \'localhost\'.'),
            'newsletter_subscribe_mail_smtp_port': gettext_lazy('25 for cleartext connection, 587 for STARTTLS, 465 for TLS. Prefer TLS if the email server supports it.'),
            'newsletter_subscribe_mail_smtp_user': gettext_lazy('Leave empty if you don\'t use any account autentication.'),
            'newsletter_subscribe_mail_smtp_password': gettext_lazy('Leave empty if you don\'t use any account autentication.'),
            'newsletter_subscribe_mail_smtp_tls': gettext_lazy('SMTP connection encrypted via TLS, prefer this rather than STARTTLS if possible. Don\'t check both. The 2 settings are mutually exclusive.'),
            'newsletter_subscribe_mail_smtp_starttls': gettext_lazy('Connexion SMTP chiffrée via STARTTLS, préférez TLS à ce réglage. Ne pas cocher les 2. Les 2 réglages sont mutuellement exclusifs.'),
        }
        labels = {
            'name': gettext_lazy('Petition template name'),
            'text': gettext_lazy('Petition text'),
            'side_text': gettext_lazy('Side text, on top of form'),
            'target': gettext_lazy('Signature target number'),
            'linear_gradient_direction': gettext_lazy('Direction of linear gradient for background color'),
            'gradient_from': gettext_lazy('Source color for linear gradient'),
            'gradient_to': gettext_lazy('Destinatoin color for linear gradient'),
            'bgcolor': gettext_lazy('Color for monochrome background color'),
            'footer_text': gettext_lazy('Footer text'),
            'footer_links': gettext_lazy('Footer links'),
            'twitter_description': gettext_lazy('Description for Twitter/Facebook cards'),
            'twitter_image': gettext_lazy('Picture for Twitter/Facebook cards'),
            'has_newsletter': gettext_lazy('Is the petition associated with a newsletter?'),
            'newsletter_subscribe_http_data': gettext_lazy('Data structure to be sent in order to subscribe someone to the newsletter in case of HTTP method'),
            'newsletter_subscribe_http_mailfield': gettext_lazy('Name of the field which should contain the email value in the PHP data structure'),
            'newsletter_subscribe_http_url': gettext_lazy('HTTP URL for newsletter subscription'),
            'newsletter_subscribe_mail_subject': gettext_lazy('Email subject for newsletter subscription command'),
            'newsletter_subscribe_mail_from': gettext_lazy('FROM field for newsletter subscription command'),
            'newsletter_subscribe_mail_to': gettext_lazy('TO field for newsletter subscription command'),
            'newsletter_subscribe_method': gettext_lazy('Newsletter subscription method'),
            'published': gettext_lazy('Puslibhed'),
            'newsletter_text': gettext_lazy('Form label text of newsletter subscription checkbox'),
            'sign_form_footer': gettext_lazy('Sign form footer text'),
            'org_twitter_handle': gettext_lazy('Organization Twitter handle'),
            'use_custom_email_settings': gettext_lazy('Use custom e-mail settings?'),
            'confirmation_email_reply': gettext_lazy('Confirmation email Reply-to address'),
            'newsletter_subscribe_mail_smtp_host': gettext_lazy('SMTP server hostname'),
            'newsletter_subscribe_mail_smtp_port': gettext_lazy('SMTP port'),
            'newsletter_subscribe_mail_smtp_user': gettext_lazy('SMTP username'),
            'newsletter_subscribe_mail_smtp_password': gettext_lazy('SMTP password'),
            'newsletter_subscribe_mail_smtp_tls': gettext_lazy('SMTP via TLS?'),
            'newsletter_subscribe_mail_smtp_starttls': gettext_lazy('SMTP via STARTTLS?'),
        }


@admin.register(PetitionTemplate)
class PetitionTemplateAdmin(admin.ModelAdmin):
    #change_form_template = 'petition/petition_change_form.html'
    form = PetitionTemplateForm
    fieldsets = (
        (gettext_lazy('To whom is this petition template?'),
         {
             'fields': ('org', 'user')
         }
         ),
         (gettext_lazy('Content of the petition'),
          {
           'fields': ('name', 'text', 'side_text', 'footer_text', 'footer_links', 'sign_form_footer', 'target')
          }
         ),
         (gettext_lazy('Background color'),
          {
              'fields': ('linear_gradient_direction', 'gradient_from', 'gradient_to', 'bgcolor')
          }
          ),
         (gettext_lazy('Setup of the newsletter associated to the petition'),
          {
              'fields': ('has_newsletter', 'newsletter_text', 'newsletter_subscribe_method',
                         'newsletter_subscribe_http_data', 'newsletter_subscribe_http_mailfield',
                         'newsletter_subscribe_http_url', 'newsletter_subscribe_mail_subject',
                         'newsletter_subscribe_mail_from', 'newsletter_subscribe_mail_to',
                         'newsletter_subscribe_mail_smtp_host', 'newsletter_subscribe_mail_smtp_port',
                         'newsletter_subscribe_mail_smtp_user', 'newsletter_subscribe_mail_smtp_password',
                         'newsletter_subscribe_mail_smtp_tls', 'newsletter_subscribe_mail_smtp_starttls')
          }
          ),
         (gettext_lazy('Confirmation email setup'),
          {
              'fields': ('confirmation_email_reply', )
          }
         ),
         (gettext_lazy('Petition meta-data for social networks'),
          {
              'fields': ('twitter_description', 'twitter_image', 'org_twitter_handle')
          }),
    )


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    pass
