from django.contrib import admin
from django.forms import ModelForm
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.core.exceptions import ValidationError

from .models import Signature, Petition
from .views import send_confirmation_email


def confirm(modeladmin, request, queryset):
    try:
        for signature in queryset:
            signature.confirm()
            signature.save()
    except ValidationError as e:
        messages.error(request, _("Error: {}").format(e.message))


def resend_confirmation_mail(modeladmin, request, queryset):
    for signature in queryset:
        send_confirmation_email(request, signature)


confirm.short_description = _("Confirm the signatures")
resend_confirmation_mail.short_description = _("Send the confirmation email once again")


@admin.register(Signature)
class SignatureAdmin(admin.ModelAdmin):
    list_display =  ('first_name', 'last_name', 'phone', 'email', 'confirmed', 'subscribed_to_mailinglist', 'petition', 'date')
    list_filter = ('petition', 'confirmed')
    actions = [confirm, resend_confirmation_mail]
    search_fields = ('first_name', 'last_name', 'phone', 'email')
    change_form_template = 'petition/signature_change_form.html'


class PetitionForm(ModelForm):
    class Meta:
        model = Petition
        fields = '__all__'
        help_texts = {
            'linear_gradient_direction': _('This is a gradient color. If selected, the background color will be a gradient color. If not, the background color will be a monochrome background color.'),
            'gradient_to': _('Only used if gradient is selected'),
            'gradient_from': _('Only used if gradient is selected'),
            'footer_links': _('Put a bullet point list of links, it will appear horizontally in the page footer'),
            'twitter_description': _('This is the description of the petition, it will be displayed in Twitter/Facebook cards when the link is posted to social networks. To be tested via https://cards-dev.twitter.com/validator and https://developers.facebook.com/tools/debug/'),
            'twitter_image': _('Picture displayed in Twitter/Facebook cards when the link is posted to social networks. To be tested via https://cards-dev.twitter.com/validator and https://developers.facebook.com/tools/debug/'),
            'has_newsletter': _('Allow to chose whether the newsletter subscription checkbox is shown or not'),
            'newsletter_subscribe_http_data': _("""Only in case subscription to the newsletter via HTTP POST or GET methods. Put here data to be sent, using Python dictionary syntax. e.g.: <br>
                    {\'_wpcf7\': 21,<br>
                    \'_wpcf7_version\': \'4.9\',<br>
                    \'_wpcf7_locale\': \'fr_FR\',<br>
                    \'_wpcf7_unit_tag\': \'wpcf7-f21-p5398-o1\',<br>
                    \'_wpcf7_container_post': \'5398\',<br>
                    \'your-email\': \'\'<br>
                    }"""),
            'newsletter_subscribe_http_mailfield': _('Only when HTTP POST or GET subscription method is used. Name of the field to send via GET or POST, containing the email address to subscribe. Following the example of preceding form field, that would be \'your-email\''),
            'newsletter_subscribe_http_url': _('Only when HTTP POST or GET subscription method is used. Adresse HTTP à requêter via GET ou POST pour enregistrer quelqu\'un sur la newsletter'),
            'newsletter_subscribe_mail_subject': _('Only when EMAIL subscription method is used. Inscrire ici la syntaxe de sujet du mail qui permet d\'inscrire quelqu\'un à la newsletter. Indiquez {} à la place où le mail du signataire doit être inséré. Ex: \'ADD NOM_LISTE {} NOM_SIGNATAIRE\''),
            'newsletter_subscribe_mail_from': _('Only when EMAIL subscription method is used. L\'expéditeur du mail qui permet d\'enregistrer quelqu\'un à la newsletter. Il s\'agit généralement d\'une adresse qui est administratrice de la liste SYMPA ou MAILMAN'),
            'newsletter_subscribe_mail_to': _('Only when EMAIL subscription method is used. Adresse email d\'administration de la liste, ex : sympa@NOM_LISTE.listes.vox.coop'),
            'newsletter_subscribe_method': _('This selects the newsletter subscription method. It is either HTTP GET or POST or via sending EMAIL to the newsletter admin address'),
            'published': _('If checked, the petition is published and accessible on the website by everybody. If not checked, the petition is only accessible by logged in users, others will get a 404 error.'),
            'newsletter_text': _('E.g.: I want to receive updates or informations from this organization.'),
            'sign_form_footer': _('E.g.: Your data will stay strictly confidential and will not be sold, given away or exchanged with third parties. Informations about this campaign as well as other news about this organization will be sent to you if you checked the checkbox. You can unsubscribe at any moment.'),
            'org_twitter_handle': _('The twitter account handle of the organization, starting with the \'@\' symbol. E.g.: @RAP_Asso. This is necessary in order to attribute the \'Twitter Card\' to the correct account. See https://developer.twitter.com/en/docs/tweets/optimize-with-cards/overview/summary'),
            'confirmation_email_sender': _('e.g.: petition@mydomain.tld'),
            'confirmation_email_smtp_host': _('If you don\'t have a real email account, leave \'localhost\'.'),
            'confirmation_email_smtp_port': _('25 for cleartext connection, 587 for STARTTLS, 465 for TLS. Prefer TLS if the email server supports it.'),
            'confirmation_email_smtp_user': _('Leave empty if you don\'t use any account autentication.'),
            'confirmation_email_smtp_password': _('Leave empty if you don\'t use any account autentication.'),
            'confirmation_email_smtp_tls': _('Connexion SMTP chiffrée via TLS, préférez ce réglage à STARTTLS. Ne pas cocher les 2. Les 2 réglages sont mutuellement exclusifs.'),
            'confirmation_email_smtp_starttls': _('Connexion SMTP chiffrée via STARTTLS, préférez TLS à ce réglage. Ne pas cocher les 2. Les 2 réglages sont mutuellement exclusifs.'),
            'newsletter_subscribe_mail_smtp_host': _('If you don\'t have a real email account, leave \'localhost\'.'),
            'newsletter_subscribe_mail_smtp_port': _('25 for cleartext connection, 587 for STARTTLS, 465 for TLS. Prefer TLS if the email server supports it.'),
            'newsletter_subscribe_mail_smtp_user': _('Leave empty if you don\'t use any account autentication.'),
            'newsletter_subscribe_mail_smtp_password': _('Leave empty if you don\'t use any account autentication.'),
            'newsletter_subscribe_mail_smtp_tls': _('SMTP connection encrypted via TLS, prefer this rather than STARTTLS if possible. Don\'t check both. The 2 settings are mutually exclusive.'),
            'newsletter_subscribe_mail_smtp_starttls': _('Connexion SMTP chiffrée via STARTTLS, préférez TLS à ce réglage. Ne pas cocher les 2. Les 2 réglages sont mutuellement exclusifs.'),
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
            'newsletter_subscribe_http_data': _('Data structure to be sent in order to subscribe someone to the newsletter in case of HTTP method'),
            'newsletter_subscribe_http_mailfield': _('Name of the field which should contain the email value in the PHP data structure'),
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


@admin.register(Petition)
class PetitionAdmin(admin.ModelAdmin):
    change_form_template = 'petition/petition_change_form.html'
    form = PetitionForm
    search_fields = ('title', )
    list_display = ('raw_title', 'non_confirmed_signature_number', 'confirmed_signature_number')
    fieldsets = (
        (_('Content of the petition'),
         {
          'fields': ('title', 'text', 'side_text', 'footer_text', 'footer_links', 'sign_form_footer', 'target')
         }
        ),
        (_('Background color'),
         {
             'fields': ('linear_gradient_direction', 'gradient_from', 'gradient_to', 'bgcolor')
         }
         ),
        (_('Setup of the newsletter associated to the petition'),
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
        (_('Confirmation email setup'),
         {
             'fields': ('confirmation_email_sender', 'confirmation_email_smtp_host', 'confirmation_email_smtp_port',
                        'confirmation_email_smtp_user', 'confirmation_email_smtp_password',
                        'confirmation_email_smtp_tls', 'confirmation_email_smtp_starttls')
         }
        ),
        (_('Petition meta-data for social networks'),
         {
             'fields': ('twitter_description', 'twitter_image', 'org_twitter_handle')
         }),
        (_('Publish the petition'),
         {
             'fields': ('published', )
         })
    )

    def non_confirmed_signature_number(self, petition):
        return petition.get_signature_number(confirmed=False)
    non_confirmed_signature_number.short_description = _('Unconfirmed signatures')

    def confirmed_signature_number(self, petition):
        return petition.get_signature_number(confirmed=True)
    confirmed_signature_number.short_description = _('Confirmed signatures')

    def raw_title(self, petition):
        return petition.raw_title
    raw_title.short_description = 'Titre'
