from django.contrib import admin
from django.forms import ModelForm, TextInput


from .models import Signature, Petition
from .views import send_confirmation_email


def confirm(modeladmin, request, queryset):
    queryset.update(confirmed=True)


def resend_confirmation_mail(modeladmin, request, queryset):
    for signature in queryset:
        send_confirmation_email(request, signature)


confirm.short_description = "Confirmer les signatures"
resend_confirmation_mail.short_description = "Renvoyer le mail de confirmation"


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
            'linear_gradient_direction': 'Un gradient est un dégradé de couleurs, s\'il est sélectionné le fond aura un dégradé de couleur, sinon la couleur de fond unie sera utilisée',
            'gradient_to': 'Uniquement utilisé si un gradient est utilisé',
            'gradient_from': 'Uniquement utilisé si un gradient est utilisé',
            'footer_links': 'Mettez une liste (avec des puces) de liens, elle apparaitra en horizontal en bas de la page',
            'twitter_description': 'Description affichée par les vignettes Twitter/Facebook, à tester via https://cards-dev.twitter.com/validator et https://developers.facebook.com/tools/debug/',
            'twitter_image': 'Image affichée par les vignettes Twitter/Facebook, à tester via https://cards-dev.twitter.com/validator et https://developers.facebook.com/tools/debug/',
            'has_newsletter': 'Permet de choisir si on affiche la case à cocher pour inviter le signataire à s\'inscrire à la newsletter',
            'newsletter_subscribe_http_data': """Uniquement en cas d\'inscription à la newsletter par la méthode HTTP POST ou GET, mettre ici les données à envoyer sous forme de dictionnaire Python. Ex: <br>
                    {\'_wpcf7\': 21,<br>
                    \'_wpcf7_version\': \'4.9\',<br>
                    \'_wpcf7_locale\': \'fr_FR\',<br>
                    \'_wpcf7_unit_tag\': \'wpcf7-f21-p5398-o1\',<br>
                    \'_wpcf7_container_post': \'5398\',<br>
                    \'your-email\': \'\'<br>
                    }""",
            'newsletter_subscribe_http_mailfield': 'Uniquement en cas d\'inscription via HTTP POST ou GET. nom du champ à envoyer via GET ou POST qui contient l\'email à inscrire, selon l\'exemple du champs précédent cela serait \'your-email\'',
            'newsletter_subscribe_http_url': 'Uniquement en cas d\'inscription via HTTP POST ou GET. Adresse HTTP à requêter via GET ou POST pour enregistrer quelqu\'un sur la newsletter',
            'newsletter_subscribe_mail_subject': 'Uniquement en cas d\'inscription à la newsletter via la méthode EMAIL. Inscrire ici la syntaxe de sujet du mail qui permet d\'inscrire quelqu\'un à la newsletter. Indiquez {} à la place où le mail du signataire doit être inséré. Ex: \'ADD NOM_LISTE {} NOM_SIGNATAIRE\'',
            'newsletter_subscribe_mail_from': 'Uniquement en cas d\'inscription à la newsletter via la méthode EMAIL. L\'expéditeur du mail qui permet d\'enregistrer quelqu\'un à la newsletter. Il s\'agit généralement d\'une adresse qui est administratrice de la liste SYMPA ou MAILMAN',
            'newsletter_subscribe_mail_to': 'Uniquement en cas d\'inscription à la newsletter via la méthode EMAIL. Adresse email d\'administration de la liste, ex : sympa@NOM_LISTE.listes.vox.coop',
            'newsletter_subscribe_method': 'Sélectionne la méthode utilisée pour inscrire quelqu\'un sur la newsletter. Soit HTTP GET ou POST ou via l\'envoie d\'un MAIL',
            'published': 'Si coché, la pétition est publiée et accessible sur le site',
            'newsletter_text': 'Ex: Je veux recevoir des informations de la part de RAP.',
            'sign_form_footer': 'Ex: Vos données resteront strictement confidentielles et ne seront ni vendues ni échangées. Des informations sur cette campagne ainsi que d’autres actualités sur RAP vous seront envoyées si vous avez coché la case. Vous pouvez vous désinscrire à tout moment.',
            'org_twitter_handle': 'Le compte Twitter de l\'organisation, précédé du @. Ex: @RAP_Asso. Nécessaire pour attribuer la \'Twitter Card\' au bon compte. Cf https://developer.twitter.com/en/docs/tweets/optimize-with-cards/overview/summary'
        }
        labels = {
            'title': 'Titre de la pétition',
            'text': 'Texte de la pétition',
            'background': 'Image de fond (non fonctionnel)',
            'mobile_background': 'Image de fond pour téléphone mobile (non fonctionnel)',
            'top_picture': 'Image en haut de la pétition (non fonctionnel)',
            'side_text': 'Texte à droite de la pétition, au dessus du formulaire',
            'target': 'Cible en nombre de signataires',
            'linear_gradient_direction': 'Direction du gratient linéaire de couleur de fond',
            'gradient_from': 'couleur d\'origine du gradient',
            'gradient_to': 'couleur de destination du gradient',
            'bgcolor': 'couleur de fond unie',
            'footer_text': 'Texte de pied de page',
            'footer_links': 'Liens de pied de page',
            'twitter_description': 'Description pour vignette Twitter/Facebook',
            'twitter_image': 'Image pour vignette Twitter/Facebook',
            'has_newsletter': 'La pétition est associée à une newsletter ?',
            'newsletter_subscribe_http_data': 'Structure de données à envoyer en HTTP pour inscrire quelqu\'un à la newsletter',
            'newsletter_subscribe_http_mailfield': 'Nom du champ contenant l\'email dans la structure de données',
            'newsletter_subscribe_http_url': 'URL HTTP d\'inscription à la newsletter',
            'newsletter_subscribe_mail_subject': 'Sujet du mail d\'inscription à la newsletter',
            'newsletter_subscribe_mail_from': 'Expéditeur du mail d\'inscription à la newsletter',
            'newsletter_subscribe_mail_to': 'Destinataire du mail d\'inscription à la newsletter',
            'newsletter_subscribe_method': 'Méthode d\'inscription à la newsletter',
            'published': 'Publiée',
            'newsletter_text': 'Texte du label de la case à cocher d\'inscription à la newsletter',
            'sign_form_footer': 'Texte sous le formulaire',
            'org_twitter_handle': 'Compte Twitter de l\'organisation'
        }


@admin.register(Petition)
class PetitionAdmin(admin.ModelAdmin):
    change_form_template = 'petition/petition_change_form.html'
    form = PetitionForm
    search_fields = ('title', )
    list_display = ('raw_title', 'non_confirmed_signature_number', 'confirmed_signature_number')

    def non_confirmed_signature_number(self, petition):
        return petition.get_signature_number(confirmed=False)
    non_confirmed_signature_number.short_description = 'Signatures non confirmées'

    def confirmed_signature_number(self, petition):
        return petition.get_signature_number(confirmed=True)
    confirmed_signature_number.short_description = 'Signatures confirmées'

    def raw_title(self, petition):
        return petition.raw_title
    raw_title.short_description = 'Titre'
