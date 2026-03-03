# -*- coding: utf-8 -*-
"""Admin page for Pytition

It defines admin actions to moderate Pytition classes such as Petitions, Users, Signatures, etc.

Also defines models that display informations about the associated class.
For example, for the `Signatures` model : user first and last name, signature status, etc.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/ref/contrib/admin/
"""

from django.contrib import admin
from django.forms import ModelForm
from django.utils.translation import gettext_lazy
from django.utils.translation import gettext as _
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Count, Max
from django import forms
from django.utils import timezone
from datetime import timedelta
from django.urls import path
from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.conf import settings
from django.db.models import Q
from django.contrib import messages

import akismet
from bs4 import BeautifulSoup

from .models import Signature, Petition, Organization, PytitionUser, PetitionTemplate, Permission, SlugModel, ModeratedElement, ModerationReason, Moderation
from .views import send_confirmation_email
from .helpers import send_moderation_mail, send_mail_to_moderation_info

### Admin actions ###

# Submit a petition as HAM with Akismet if it is not down
def submit_ham(modeladmin, request, queryset):
    for petition in queryset:
        if petition.ipaddr and petition.user_agent:
            try:
                soup = BeautifulSoup(petition.text, "html.parser")
                text_msg = soup.get_text(separator = " ")
                clean_text_msg = ' '.join(text_msg.split())

                config = akismet.Config(key=settings.AKISMET_KEY, url=settings.AKISMET_URL)
                with akismet.SyncClient(config=config) as akismet_client:
                    akismet_client.submit_ham(petition.ipaddr,
                                        user_agent = petition.user_agent,
                                        comment_type = "blog-post",
                                        comment_author = petition.user.username,
                                        comment_author_email = petition.user.user.email,
                                        comment_content = petition.title + " " + clean_text_msg,
                                        is_test = 1 if settings.DEBUG else 0) #is_test to change in production

                if petition.moderated:
                    petition.moderate(False)
                elif petition.monitored:
                    petition.monitor(False)

            except Exception as e:
                is_spam = 0
                send_mail_to_moderation_info(settings.MODERATION_EMAIL, _("Akismet is down: {e}").format(e=e))
        else:
            messages.error(request, "This petition doesn't have a stored ip address or user agent")


# Submit a petition as SPAM with Akismet if is not down
# moderate the petitions and send emails to admin and user
def submit_spam(modeladmin, request, queryset):
    for petition in queryset:
        if petition.ipaddr and petition.user_agent:
            try:
                soup = BeautifulSoup(petition.text, "html.parser")
                text_msg = soup.get_text(separator = " ")
                clean_text_msg = ' '.join(text_msg.split())
                
                config = akismet.Config(key=settings.AKISMET_KEY, url=settings.AKISMET_URL)
                with akismet.SyncClient(config=config) as akismet_client:
                    akismet_client.submit_spam(petition.ipaddr,
                                        user_agent = petition.user_agent,
                                        comment_type = "blog-post",
                                        comment_author = petition.user.username,
                                        comment_author_email = petition.user.user.email,
                                        comment_content = petition.title + " " + clean_text_msg,
                                        is_test = 1 if settings.DEBUG else 0) #is_test to change in production

                petition.moderate(True)
                moderation_reason = ModerationReason.objects.create(msg="This petition is inappropriate.", visible=True)
                moderation = Moderation.objects.create(petition=petition, reason=moderation_reason)

                if petition.user:
                    send_moderation_mail(petition.user.user.email, petition.user.user.username, moderation.reason.text, "petition", petition)
                elif petition.org:
                    for member in petition.org.members.all():
                        permissions = Permission.objects.get(organization=petition.org, user=member)
                        if permissions:
                            if permissions.can_modify_permissions:
                                send_moderation_mail(member.user.email, member.user.username, moderation.reason.text, "petition", petition)

            except Exception as e:
                is_spam = 0
                send_mail_to_moderation_info(settings.MODERATION_EMAIL, _("Akismet is down: {e}").format(e=e))

        else:
            messages.error(request, "This petition doesn't have a stored ip address or user agent")

    
# Confirm the signatures of selected petitions
def confirm(modeladmin, request, queryset):
    try:
        for signature in queryset:
            signature.confirm()
            signature.save()
    except ValidationError as e:
        messages.error(request, gettext_lazy("Error: {}").format(e.message))


# Resend confirmation email for selected petitions
def resend_confirmation_mail(modeladmin, request, queryset):
    for signature in queryset:
        send_confirmation_email(request, signature)


# Publish selected petitions
def publish_petition(modeladmin, request, queryset):
    for petition in queryset:
        petition.publish()


# Switch selected petitions status between 'moderated' and 'not moderated'
# if we moderate a petition, we send an email to the owner of the petition: user or org member
def moderate_petition(modeladmin, request, queryset):
    moderation_reason, created = ModerationReason.objects.get_or_create(msg="manual_moderation")

    for petition in queryset:
        petition.moderate(not(petition.moderated))

        if petition.moderated:
            petition.monitor(False)
            moderation = Moderation.objects.create(petition=petition, reason=moderation_reason)
            if petition.user:
                send_moderation_mail(petition.user.user.email, petition.user.user.username, moderation.reason.text, "petition", petition)
            elif petition.org:
                for member in petition.org.members.all():
                    permissions = Permission.objects.get(organization=petition.org, user=member)
                    if permissions:
                        if permissions.can_modify_permissions:
                            send_moderation_mail(member.user.email, member.user.username, moderation.reason.text, "petition", petition)

# Switch selected elements status between 'moderated' and 'not moderated'
# if we moderate an element, we send an email to the user, the org or the owner of the petition depending on the type of the element in the queryset
def moderate_element(modeladmin, request, queryset):
    moderation_reason, created = ModerationReason.objects.get_or_create(msg="manual_moderation")

    for element in queryset:
        element.moderate(not(element.moderated))
        if element.moderated:
            element.monitor(False)

            if isinstance(element, Petition):
                moderation = Moderation.objects.create(petition=element, reason=moderation_reason)
                if element.user:
                    send_moderation_mail(element.user.user.email, element.user.user.username, moderation.reason.text, "petition", element)
                elif element.org:
                    for member in element.org.members.all():
                        permissions = Permission.objects.get(organization=element.org, user=member)
                        if permissions:
                            if permissions.can_modify_permissions:
                                send_moderation_mail(member.user.email, member.user.username, moderation.reason.text, "petition", element)
            
            elif isinstance(element, Organization):
                moderation = Moderation.objects.create(org=element, reason=moderation_reason)
                for member in element.members.all():
                    permissions = Permission.objects.get(organization=element, user=member)
                    if permissions:
                        if permissions.can_modify_permissions:
                            send_moderation_mail(member.user.email, member.user.username, moderation.reason.text, "organization", element)
            
            elif isinstance(element, PytitionUser):
                moderation = Moderation.objects.create(user=element, reason=moderation_reason)
                send_moderation_mail(element.user.email, element.user.username, moderation.reason.text, "user", element)
        else:
            moderations = element.moderation.all()
            for moderation in moderations:
                moderation.delete()

# Remove a report for a petition
def ignore_report(modeladmin, request, queryset):
    for element in queryset:
        moderations = element.moderation.all()
        for moderation in moderations:
            moderation.delete()

# Monitor selected elements
def monitor_element(modeladmin, request, queryset):
    for element in queryset:
        element.monitor(not(element.monitored))

# Unpublish selected petitions
def unpublish_petition(modeladmin, request, queryset):
    for petition in queryset:
        petition.unpublish()

# Delete selected elements
# Redirects to a custom confirmation page with information about the elements to delete
def delete_element(modeladmin, request, queryset):
    detail = True
    if request.method == "POST":
        delete_action = request.POST.get('action')
        for key in ['selected_user', 'selected_orga', 'selected_petition', 'selected_mon_petition', 'selected_mon_user', 'selected_mon_orga']:
            # If we want to delete elements from the spam monitoring page
            if key in request.POST:
                element_type = key
                detail = False

            for element in queryset:
                if element.moderated:
                    element.mod = gettext_lazy("moderated")
                    if element.moderation.last() == None:
                        element.reason = gettext_lazy("not specified")
                    else:
                        element.reason = element.moderation.last().reason.text
                elif element.monitored:
                    element.mod = gettext_lazy("monitored")
                    if element.monitoring.last() == None:
                        element.reason = gettext_lazy("not specified")
                    else:
                        element.reason = element.monitoring.last().reason.text
                
                if isinstance(element, PytitionUser):
                    element.petitions = str(list(element.petition_set.all())).replace("[", "").replace("]", "")
                    element.orgas = str(list(element.organization_set.all())).replace("[", "").replace("]", "").replace("<", "").replace(">", "")
                    element.orgs = element.organization_set.all()
                    element.delete_orgas = []
                    for org in element.orgs:
                        if org.members.count() == 1:
                            element.delete_orgas.append(org)
                    element.delete_orgas = str(list(element.delete_orgas)).replace("[", "").replace("]", "").replace("<", "").replace(">", "")

                elif isinstance(element, Organization):
                    element.members_str = str(list(element.members.all())).replace("[", "").replace("]", "")
                    element.petitions = str(list(element.petition_set.all())).replace("[", "").replace("]", "")

                elif isinstance(element, Petition):
                    if element.user:
                        element.delete_owner_type= "User"
                        element.delete_owner = element.user.username
                        element.delete_owner_id = element.user.user_id
                    else:
                        element.delete_owner_type = "Organization"
                        element.delete_owner = element.org.name
                        element.delete_owner_id = None

                    element.signature_num = element.get_signature_number()

        # If we want to delete an element from a detail page
        if detail == True:
            for element in queryset:
                if isinstance(element, PytitionUser):
                    if element.moderated:
                        element_type = "selected_user"
                    else:
                        element_type = "selected_mon_user"

                elif isinstance(element, Organization):
                    if element.moderated:
                        element_type = "selected_orga"
                    else:
                        element_type = "selected_mon_orga"

                elif isinstance(element, Petition):
                    if element.moderated:
                        element_type = "selected_petition"
                    else:
                        element_type = "selected_mon_petition"

        if request.POST.get('confirm') == 'yes':
            for element in queryset:
                if isinstance(element, PytitionUser):
                    element.drop()
                else:
                    element.delete()
            return HttpResponseRedirect(reverse('admin:moderatedelement_my_view'))

        elif request.POST.get('confirm') == 'no':
            return HttpResponseRedirect(reverse('admin:moderatedelement_my_view'))

    return TemplateResponse(
        request,
        "admin/delete.html", 
        {
            "detail": detail,
            "elements": queryset,
            "type": element_type,
            "delete_action" : delete_action,
        }
    )

# Switch petitions check_signatures_at_each_signature between True and False. If False, the number of signatures is checked periodically.
def check_periodically(modeladmin, request, queryset):
    for petition in queryset:
        petition.check_signatures_periodically(not(petition.check_signatures_at_each_signature))
        if petition.check_signatures_at_each_signature and petition.cron_to_schedule:
            petition.cron_to_schedule = False
            petition.save()
        elif not(petition.check_signatures_at_each_signature) and not(petition.cron_to_schedule):
            if petition.get_signature_number() > 0:
                petition.cron_to_schedule = True
                petition.save()

### Descriptions of each custom action in drop-down menu ###


confirm.short_description = gettext_lazy("Confirm selected signatures")
resend_confirmation_mail.short_description = gettext_lazy("Resend confirmation email")
publish_petition.short_description = gettext_lazy("Publish selected petitions")
moderate_petition.short_description = gettext_lazy("Moderate selected petitions")
unpublish_petition.short_description = gettext_lazy("Unpublish selected petitions")
delete_element.short_description = gettext_lazy("Delete selected elements")
check_periodically.short_description = gettext_lazy("Switch between bot testing periodically and at each signature")
moderate_element.short_description = gettext_lazy("Moderate selected elements")
submit_spam.short_description = gettext_lazy("Submit spam")
submit_ham.short_description = gettext_lazy("Submit ham")
ignore_report.short_description = gettext_lazy("Ignore selected petition report")

### ModelAdmin classes ###


@admin.register(PytitionUser)
class PytitionUserAdmin(admin.ModelAdmin):
    # Displays the name of the user, their petition numbers and if they are moderated
    # Can filter by moderation
    list_display = ('name', 'petition_number', 'day_petition_number', 'is_moderated')
    list_filter = ('moderated',)
    actions = [moderate_element]

    # User name
    def name(self, pu):
        return pu
    name.description = gettext_lazy("Name")

    def get_queryset(self, request):
        # overload queryset and annotate it to compute petitions number
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            total_petition_count=Count('petition'),
            day_petition_count=Count('petition',
                filter=(
                    models.Q(petition__publication_date__gte=timezone.now() - timedelta(days=1))))
            )
        return queryset

    # User number of petitions from get_queryset
    def petition_number(self, pu):
        return pu.total_petition_count
    petition_number.short_description = gettext_lazy('Number of petitions')

    # User number of petitions in 24h from get_queryset
    def day_petition_number(self, pu):
        return pu.day_petition_count
    day_petition_number.short_description = gettext_lazy('Number of petitions in 24h')

    # Returns the moderation status
    def is_moderated(self, pu):
        return pu.moderated

@admin.register(SlugModel)
class SlugModelAdmin(admin.ModelAdmin):
    pass


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    # Displays the name of the organization, its petition numbers, its total number of users, its number of moderated users and if it is moderated
    # Can filter by moderation
    list_display = ('name', 'petition_num', 'day_petition_num', 'user_num', 'num_moderated_members', 'org_is_moderated')
    list_filter = ('moderated',)
    actions = [moderate_element]

    def get_queryset(self, request):
        # overload queryset and annotate it to compute petitions number
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            total_petition_count_org=Count('petition'),
            day_petition_count_org=Count('petition',
                filter=(
                    models.Q(petition__publication_date__gte=timezone.now() - timedelta(days=1)))),
            user_num = Count('members', distinct=True),
            num_mod_members = Count('members', 
                filter=(
                    models.Q(members__moderated=True)
                ), distinct=True,)
            )
        return queryset
    
    # Total petition number
    def petition_num(self, org):
        return org.total_petition_count_org

    # Number of petitions in one day
    def day_petition_num(self, org):
        return org.day_petition_count_org

    # Number of users
    def user_num(self, org):
        return org.user_num

    #Number of moderated members and moderation of members (we might want to change the position of this function)
    def num_moderated_members(self, org):
        return org.num_mod_members

    petition_num.description = gettext_lazy('Number of petitions')
    user_num.description = gettext_lazy('Number of members')

    # Returns the moderation status
    def org_is_moderated(self, org):
        return org.moderated

@admin.register(Signature)
class SignatureAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone', 'email', 'confirmed', 'subscribed_to_mailinglist', 'petition', 'date')
    list_filter = ('petition', 'confirmed')
    actions = [confirm, resend_confirmation_mail]

    # fields to search threw when searching by keyword in admin panel
    search_fields = ('first_name', 'last_name', 'phone', 'email')
    change_form_template = 'petition/signature_change_form.html'


#class SlugInlineAdmin(admin.TabularInline):
    #Petition.slugs.through


# Petition Form used in the `Petitions` section of the admin page
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
            'published': gettext_lazy('Published'),
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

    """
    Overload queryset
    so we can filter petitions in admin page
    according to their number of signature
    
    If queryset isnt annotated, Django doesnt allow filtering by objects
    that are not fields in the DataBase
    """
    def get_queryset(self, request):

        # overload queryset and annotate it to compute signatures number
        queryset = super().get_queryset(request)
        today = timezone.now()
        yesterday_start = today - timedelta(days=1)
        yesterday_end = today
        queryset = queryset.annotate(
            publication_date_ano=Max('publication_date'),
            total_signature_count=Count('signature'),
            day_signature_count=Count('signature',
                filter=(
                    models.Q(signature__date__gte=timezone.now() - timedelta(days=1)))),
            week_signature_count=Count('signature',
                filter=(
                    models.Q(signature__date__gte=timezone.now() - timedelta(weeks=1)))),
            month_signature_count=Count('signature',
                filter=(
                    models.Q(signature__date__gte=timezone.now() - timedelta(weeks=4)))),
            yesterday_signature_count = Count('signature',
                filter=(
                    models.Q(signature__date__gte=yesterday_start, signature__date__lt=yesterday_end)))
            )
            
        return queryset


    # fields to search threw when searching by keyword in admin panel
    search_fields = ('title', )

    # petition attributes to display in admin panel
    list_display = ('title', 'publication_date_translated', 'total_signature_number', 'day_signature_number', 'day_before_signature_number', 'week_signature_number', 'month_signature_number', 'status')

    # petition moderation actions
    actions = [publish_petition, moderate_petition, unpublish_petition, submit_spam, submit_ham]
    
    # form used to modify a petition
    change_form_template = 'petition/petition_change_form.html'
    form = PetitionAdminForm

    # fieldsets used in petition form
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


    ### Custom list displays for PetitionAdmin class ###


    # return petition status
    # 'Published', 'Not Published', 'Moderated'
    def status(self, petition):
        if (petition.moderated):
            return "Moderated"
        if (petition.published):
            return "Published"
        return "Not Published"

    # description of this attribute in the admin page
    status.short_description = gettext_lazy('Status')


    # return the petition publication date
    # used to be able to translate the description string 
    def publication_date_translated(self, petition):
        return petition.publication_date_ano

    # enable sorting by this attribute in admin page
    publication_date_translated.admin_order_field = 'publication_date_ano'
    publication_date_translated.short_description = gettext_lazy('Publication date')


    # return the petition total number of signatures
    def total_signature_number(self, petition):
        return petition.total_signature_count
    total_signature_number.admin_order_field = 'total_signature_count'
    total_signature_number.short_description = gettext_lazy('Total number of signatures')


    # return the petition number of signatures today
    def day_signature_number(self, petition):
        return petition.day_signature_count
    day_signature_number.admin_order_field = 'day_signature_count'
    day_signature_number.short_description = gettext_lazy('Number of signatures since one day')

    # return the petition number of signatures yesterday
    def day_before_signature_number(self, petition):
        return petition.yesterday_signature_count
    day_before_signature_number.short_description = gettext_lazy('Number of signatures yesterday')

    # return the petition number of signatures since one week
    def week_signature_number(self, petition):
        return petition.week_signature_count
    week_signature_number.admin_order_field = 'week_signature_count'
    week_signature_number.short_description = gettext_lazy('Number of signatures since one week')


    # return the petition number of signatures since one month
    def month_signature_number(self, petition):
        return petition.month_signature_count
    month_signature_number.admin_order_field = 'month_signature_count'
    month_signature_number.short_description = gettext_lazy('Number of signatures since one month')


# Petition Template Form used in the `Petition Templates` section of the admin page
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
            'published': gettext_lazy('Published'),
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

# Spam monitoring page
@admin.register(ModeratedElement)
class SpamMonitoringAdmin(admin.ModelAdmin):

    actions = [unpublish_petition, publish_petition, ignore_report, moderate_element, delete_element, check_periodically, submit_ham, submit_spam, monitor_element]
    
    # annotate the queryset to get data from the users for the html page
    def annotate_users_with_status(self, users_queryset):
        users_queryset = users_queryset.annotate(
            day_num_petitions = Count('petition',
                filter=(
                    models.Q(petition__publication_date__gte=timezone.now() - timedelta(days=1)))),
            num_petitions = Count('petition'),
            num_monitored_petitions = Count('petition',
                filter=(
                    models.Q(Q(petition__monitored=True) | Q(petition__moderated=True))
                ))
        )

        for user in users_queryset:
            user.signature_num = user.get_total_signature_number()
            if user.moderated:
                if user.moderation.last().reason == None:
                    user.mod_reason = gettext_lazy("not specified")
                else:
                    user.mod_reason = user.moderation.last().reason.text
            elif user.monitored:
                if user.monitoring.last().reason == None:
                    user.mon_reason = gettext_lazy("not specified")
                    user.priority = "not specified"
                else:
                    user.mon_reason = user.monitoring.last().reason.text
                    user.priority = user.monitoring.last().priority
                
                if user.priority == "strong":
                    user.color = "#ffa7a7"
                elif user.priority == "average":
                    user.color = "#ffd2a7"
                elif user.priority == "low":
                    user.color = "#ffffa7"

        return users_queryset

    #annotate the queryset to get data from the organizations for the html page
    def annotate_orgs_with_status(self, orgs_queryset):
        orgs_queryset = orgs_queryset.annotate(
            day_num_petitions = Count('petition',
                filter=(
                    models.Q(petition__publication_date__gte=timezone.now() - timedelta(days=1)))),
            num_petitions = Count('petition', distinct=True),
            num_monitored_petitions = Count('petition',
                filter=(
                    models.Q(Q(petition__monitored=True) | Q(petition__moderated=True))
                )),
            user_num = Count('members', distinct=True),
            num_mod_members = Count('members', 
                filter=(
                    models.Q(members__moderated=True)
                ), distinct=True,)
        )

        for org in orgs_queryset:
            org.signature_num = org.get_total_signature_number()
            if org.moderated:
                if org.moderation.last() == None or org.moderation.last().reason == None:
                    org.mod_reason = gettext_lazy("not specified")
                else:
                    org.mod_reason = org.moderation.last().reason.text
            elif org.monitored:
                if org.monitoring.last() == None or org.monitoring.last().reason == None:
                    org.mon_reason = gettext_lazy("not specified")
                    org.priority = "not specified"
                else:
                    org.mon_reason = org.monitoring.last().reason.text
                    org.priority = org.monitoring.last().priority
                
                if org.priority == "strong":
                    org.color = "#ffa7a7"
                elif org.priority == "average":
                    org.color = "#ffd2a7"
                elif org.priority == "low":
                    org.color = "#ffffa7"

        return orgs_queryset

    #annotate the queryset to get data from the petitions for the html page
    def annotate_petitions_with_status(self, petitions_queryset):
        petitions_queryset = petitions_queryset.annotate(
            signature_num = Count('signature'),
            unconfirmed_num = Count('signature', 
                filter=(
                    models.Q(signature__confirmed=False, signature__date__gte = timezone.now() - timedelta(hours=6)))),
            day_num_signatures = Count('signature',
                filter=(
                    models.Q(signature__date__gte=timezone.now() - timedelta(days=1)))),
            yesterday_num_signatures = Count('signature',
                filter=(
                    models.Q(signature__date__gte=timezone.now() - timedelta(days=1), signature__date__lt=timezone.now()))),
        )

        for petition in petitions_queryset:
            if petition.moderated:
                if petition.moderation.last().reason == None:
                    petition.mod_reason = gettext_lazy("not specified")
                else:
                    petition.mod_reason = petition.moderation.last().reason.text

            if petition.monitored:
                if petition.monitoring.last().reason == None:
                    petition.mon_reason = gettext_lazy("not specified")
                    petition.priority = "not specified"
                else:
                    petition.mon_reason = petition.monitoring.last().reason.text
                    petition.priority = petition.monitoring.last().priority

                if petition.priority == "strong":
                    petition.color = "#ffa7a7"
                elif petition.priority == "average":
                    petition.color = "#ffd2a7"
                elif petition.priority == "low":
                    petition.color = "#ffffa7"

        return petitions_queryset

    def annotate_reported_petitions_with_status(self, reported_petitions_list):
        reported_petitions = []
        for petition in reported_petitions_list:
            p = Petition.objects.get(pk=petition['petition'])
            reported_petitions.append(p)

            # Get the clean text of the petition to display it
            n = 50
            soup = BeautifulSoup(p.text, "html.parser")
            text_msg = soup.get_text(separator = " ")
            clean_text_msg = ' '.join(text_msg.split())
            cut_text_list = clean_text_msg.split()[:n]
            p.cut_text_str = " ".join(cut_text_list)
            if p.moderation.last().reason:
                p.rep_reason = p.moderation.last().reason.text
            else:
                p.rep_reason = gettext_lazy("not specified")
            p.num_rep = p.moderation.count()
        return reported_petitions

    # returns the moderated users with an initial limit of 50
    def get_moderated_users(self, request, limit=50):
        moderated_users = PytitionUser.objects.filter(moderated=True)[:limit]
        moderated_users = self.annotate_users_with_status(moderated_users)
        return moderated_users

    # returns the monitored users with an initial limit of 50
    def get_monitored_users(self, request, limit=50):
        monitored_users = PytitionUser.objects.filter(monitored=True)[:limit]
        monitored_users = self.annotate_users_with_status(monitored_users)
        return monitored_users

    # returns the moderated organizations with an initial limit of 50
    def get_moderated_organizations(self, request, limit=50):
        moderated_organizations = Organization.objects.filter(moderated=True)[:limit]
        moderated_organizations = self.annotate_orgs_with_status(moderated_organizations)
        return moderated_organizations

    # returns the monitored organizations with an initial limit of 50
    def get_monitored_organizations(self, request, limit=50):
        monitored_organizations = Organization.objects.filter(monitored=True)[:limit]
        monitored_organizations = self.annotate_orgs_with_status(monitored_organizations)
        return monitored_organizations

    # returns the moderated petitions with an initial limit of 50
    def get_moderated_petitions(self, request, limit=50):
        moderated_petitions = Petition.objects.filter(moderated=True).order_by('-creation_date')[:limit]
        moderated_petitions = self.annotate_petitions_with_status(moderated_petitions)
        return moderated_petitions

    # returns the monitored petitions with an initial limit of 50
    def get_monitored_petitions(self, request, limit=50):
        monitored_petitions = Petition.objects.filter(monitored=True).order_by('-creation_date')[:limit]
        monitored_petitions = self.annotate_petitions_with_status(monitored_petitions)
        return monitored_petitions

    # returns the reported petitions with an initial limit of 50
    def get_reported_petitions(self, request, limit=50):
        reported_petitions = Moderation.objects.values('petition').annotate(count=Count('petition')).filter(petition__moderated=False).order_by('-count')[:limit]
        reported_petitions = self.annotate_reported_petitions_with_status(reported_petitions)
        return reported_petitions

    # redirects to html template admin/spam_page.html
    def changelist_view(self, request, extra_context=None):
        url = reverse('admin:moderatedelement_my_view')
        return HttpResponseRedirect(url)

    # defines the url of the custom view
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [path("my_view/", self.admin_site.admin_view(self.my_view), name = 'moderatedelement_my_view'),
                   path('custom-petition/<int:petition_id>/<owner>/<str:owner_type>/', self.admin_site.admin_view(self.custom_petition_detail), name='custom_petition_detail'),
                   path('custom-user/<str:user>/', self.admin_site.admin_view(self.custom_user_detail), name='custom_user_detail'),
                   path('custom-org/<str:orga>/', self.admin_site.admin_view(self.custom_org_detail), name='custom_org_detail'),]
        return my_urls + urls

    # defines the custom view "spam monitoring page" and the context we send
    def my_view(self, request):
        # Define the available actions for each table depending on the type of element
        actions  = self.get_actions(request)
        actions_user = [gettext_lazy("demoderate user"), gettext_lazy("delete user")]
        actions_org = [gettext_lazy("demoderate organization"), gettext_lazy("delete organization")]
        actions_mon_user = [gettext_lazy("demonitor user"), gettext_lazy("moderate user"), gettext_lazy("delete user")]
        actions_mon_org = [gettext_lazy("demonitor organization"), gettext_lazy("moderate organization"), gettext_lazy("delete organization")]
        actions_mon_petition = [gettext_lazy("demonitor petition"), gettext_lazy("moderate petition"), gettext_lazy("delete petition"), gettext_lazy("switch check signatures at each signature"), gettext_lazy("submit petition as ham"), gettext_lazy("submit petition as spam")]
        actions_mod_petitions = [gettext_lazy("demoderate petition"), gettext_lazy("delete petition"), gettext_lazy("switch check signatures at each signature"), gettext_lazy("submit petition as ham"), gettext_lazy("submit petition as spam")]
        actions_rep_petitions = [gettext_lazy("ignore report"), gettext_lazy("moderate petition"), gettext_lazy("delete petition"), gettext_lazy("submit petition as spam")]

        queryset = self.model.objects.all()
        context = dict(
            # Include useful variables for rendering the admin template.
            self.admin_site.each_context(request),
            mod_users = self.get_moderated_users(request),
            mon_users = self.get_monitored_users(request),
            mod_organizations = self.get_moderated_organizations(request),
            mon_organizations = self.get_monitored_organizations(request),
            mod_petitions = self.get_moderated_petitions(request),
            mon_petitions = self.get_monitored_petitions(request),
            rep_petitions = self.get_reported_petitions(request),
            queryset = queryset,
            actions = actions,
            actions_user = actions_user,
            actions_org = actions_org,
            actions_mon_user = actions_mon_user,
            actions_mon_org = actions_mon_org,
            actions_mon_petition = actions_mon_petition,
            actions_mod_petitions = actions_mod_petitions,
            actions_rep_petitions = actions_rep_petitions,
            signature_throttle = settings.SIGNATURE_THROTTLE,
            signature_throttle_timing = settings.SIGNATURE_THROTTLE_TIMING,
            signature_variation_critical = settings.SIGNATURE_VARIATION_CRITICAL,
            signature_variation_strong = settings.SIGNATURE_VARIATION_STRONG,
            signature_variation_average = settings.SIGNATURE_VARIATION_AVERAGE,
            signature_variation_low = settings.SIGNATURE_VARIATION_LOW,
            signature_number_critical = settings.SIGNATURE_NUMBER_CRITICAL,
            signature_number_strong = settings.SIGNATURE_NUMBER_STRONG,
            signature_number_average = settings.SIGNATURE_NUMBER_AVERAGE,
            signature_number_low = settings.SIGNATURE_NUMBER_LOW,
            unconfirmed_signature_critical = settings.UNCONFIRMED_NUMBER_CRITICAL,
            unconfirmed_signature_strong = settings.UNCONFIRMED_NUMBER_STRONG,
            unconfirmed_signature_average = settings.UNCONFIRMED_NUMBER_AVERAGE,
            unconfirmed_signature_low = settings.UNCONFIRMED_NUMBER_LOW,
            signature_at_creation_critical = settings.CREATION_NUMBER_CRITICAL,
            signature_at_creation_strong = settings.CREATION_NUMBER_STRONG,
            signature_at_creation_average = settings.CREATION_NUMBER_AVERAGE,
            signature_at_creation_low = settings.CREATION_NUMBER_LOW,
            day_petition_critical = settings.DAY_PETITION_CRITICAL,
            day_petition_strong = settings.DAY_PETITION_STRONG,
            day_petition_average = settings.DAY_PETITION_AVERAGE,
            day_petition_low = settings.DAY_PETITION_LOW,
            monitored_petitions_critical = settings.MONITORED_PETITIONS_CRITICAL,
            monitored_petitions_strong = settings.MONITORED_PETITIONS_STRONG,
            monitored_petitions_average = settings.MONITORED_PETITIONS_AVERAGE,
            monitored_petitions_low = settings.MONITORED_PETITIONS_LOW,
            signatures_total_critical = settings.SIGNATURES_TOTAL_CRITICAL,
            signatures_total_strong = settings.SIGNATURES_TOTAL_STRONG,
            signatures_total_average = settings.SIGNATURES_TOTAL_AVERAGE,
            signatures_total_low = settings.SIGNATURES_TOTAL_LOW,

        )
        
        if request.method == "POST":
            # get the number of petitions (moderated or monitored) to display in the table from the frontend
            limit_mod_value = request.POST.get('limit_mod')
            limit_mon_value = request.POST.get('limit_mon')
            limit_rep_value = request.POST.get('limit_rep')
            limit_users_value = request.POST.get('limit_users')
            limit_mon_users_value = request.POST.get('limit_mon_users')
            limit_orgas_value = request.POST.get('limit_orgas')
            limit_mon_orgas_value = request.POST.get('limit_mon_orgas')
            action_name = request.POST.get('action')

            ### Admin actions ###
            for key in ['selected_user', 'selected_orga', 'selected_petition', 'selected_mon_petition', 'selected_rep_petition', 'selected_mon_user', 'selected_mon_orga']:
                # get the queryset with the selected ids depending on the type of element
                if key in request.POST:
                    selected_ids = request.POST.getlist(key)
                    if key == "selected_user" or key == "selected_mon_user":
                        queryset = PytitionUser.objects.filter(pk__in=selected_ids)
                      
                    elif key == "selected_orga" or key == "selected_mon_orga":
                        queryset = Organization.objects.filter(pk__in=selected_ids)
                   
                    else:
                        queryset = Petition.objects.filter(pk__in=selected_ids)

                    if action_name == gettext_lazy("demoderate user") or action_name == gettext_lazy("demoderate organization") or action_name == gettext_lazy("demoderate petition")  or action_name == gettext_lazy("moderate petition") or action_name == gettext_lazy("moderate user") or action_name == gettext_lazy("moderate organization"):
                        action_name = "moderate_element"

                    elif action_name == gettext_lazy("demonitor user") or action_name == gettext_lazy("demonitor organization") or action_name == gettext_lazy("demonitor petition"):
                        action_name = "monitor_element"

                    elif action_name == gettext_lazy("delete user") or action_name == gettext_lazy("delete organization") or action_name == gettext_lazy("delete petition"):
                        action_name = "delete_element"

                    elif action_name == gettext_lazy("ignore report"):
                        action_name = "ignore_report"

                    elif action_name == gettext_lazy("submit petition as ham"):
                        action_name = "submit_ham"

                    elif action_name == gettext_lazy("submit petition as spam"):
                        action_name = "submit_spam"

                    elif action_name == gettext_lazy("switch check signatures at each signature"):
                        action_name = "check_periodically"

                    # call the selected admin action on the defined queryset
                    if action_name in actions:
                        func, _, _ = actions[action_name]
                        response = func(self, request, queryset)
                        if response:
                            return response
                        return HttpResponseRedirect(request.path)

            # update the context with the limit of moderated petitions to be displayed 
            if limit_mod_value:
                # to display all moderated petitions
                if limit_mod_value == "None":
                    limit_mod_value = None
                else:
                    limit_mod_value = int(limit_mod_value)
                    
                context.update(
                        mod_petitions= self.get_moderated_petitions(request, limit_mod_value),
                    )

            # update the context with the limit of monitored petitions to be displayed
            if limit_mon_value:
                # to display all monitored petitions
                if limit_mon_value == "None":
                    limit_mon_value = None
                else:
                    limit_mon_value = int(limit_mon_value)
                   
                context.update(
                        mon_petitions = self.get_monitored_petitions(request, limit_mon_value),
                    )

            # update the context with the limit of reported petitions to be displayed
            if limit_rep_value:
                # to display all reported petitions
                if limit_rep_value == "None":
                    limit_rep_value = None
                else:
                    limit_rep_value = int(limit_rep_value)
                   
                context.update(
                        rep_petitions = self.get_reported_petitions(request, limit_rep_value),
                    )

            # update the context with the limit of moderated users to be displayed
            if limit_users_value:
                # to display all monitored petitions
                if limit_users_value == "None":
                    limit_users_value = None
                else:
                    limit_users_value = int(limit_users_value)
                    
                context.update(
                        mod_users = self.get_moderated_users(request, limit_users_value),
                    )

            # update the context with the limit of monitored users to be displayed
            if limit_mon_users_value:
                # to display all monitored petitions
                if limit_mon_users_value == "None":
                    limit_mon_users_value = None
                else:
                    limit_mon_users_value = int(limit_mon_users_value)
                    
                context.update(
                        mon_users = self.get_monitored_users(request, limit_mon_users_value),
                    )

            # update the context with the limit of moderated organizations to be displayed
            if limit_orgas_value:
                # to display all monitored petitions
                if limit_orgas_value == "None":
                    limit_orgas_value = None
                else:
                    limit_orgas_value = int(limit_orgas_value)
                   
                context.update(
                        mod_organizations = self.get_moderated_organizations(request, limit_orgas_value),
                    )

            # update the context with the limit of monitored organizations to be displayed
            if limit_mon_orgas_value:
                # to display all monitored petitions
                if limit_mon_orgas_value == "None":
                    limit_mon_orgas_value = None
                else:
                    limit_mon_orgas_value = int(limit_mon_orgas_value)
                   
                context.update(
                        mon_organizations = self.get_monitored_organizations(request, limit_mon_orgas_value),
                    )
                  
            # reload the page to display the tables with the chosen limit
            return TemplateResponse(request, "admin/spam_page.html", context)

        return TemplateResponse(request, "admin/spam_page.html", context)

    # custom view to display petition detail when clicking on a petition in the spam monitoring page
    def custom_petition_detail(self, request, petition_id, owner, owner_type):
        actions  = self.get_actions(request)
        mod_reason = None
        mon_reason = None

        # We get the petition associated to the right owner to avoid errors when fetching a petition
        if owner_type == "org":
            petition = Petition.objects.get(id=petition_id, org=owner)
        elif owner_type == "user":
            petition = Petition.objects.get(id=petition_id, user=owner)
        
        # Get the clean text of the petition to display it
        soup = BeautifulSoup(petition.text, "html.parser")
        text_msg = soup.get_text(separator = " ")
        clean_text_msg = ' '.join(text_msg.split())

        actions_petition = [gettext_lazy("moderate petition"), gettext_lazy("delete petition"), gettext_lazy("switch check signatures at each signature"), gettext_lazy("submit petition as ham"), gettext_lazy("submit petition as spam")]

        # Get the moderation/monitoring status of the petition and the associated actions to be displayed
        if petition.moderated:
            if petition.moderation.last().reason == None:
                mod_reason = gettext_lazy("not specified")
            else:
                mod_reason = petition.moderation.last().reason.text

            actions_petition = [gettext_lazy("demoderate petition"), gettext_lazy("delete petition"), gettext_lazy("switch check signatures at each signature"), gettext_lazy("submit petition as ham"), gettext_lazy("submit petition as spam")]

        if petition.monitored:
            if petition.monitoring.last().reason == None:
                mon_reason = gettext_lazy("not specified")
            else:
                mon_reason = petition.monitoring.last().reason.text
            
            actions_petition = [gettext_lazy("demonitor petition"), gettext_lazy("moderate petition"), gettext_lazy("delete petition"), gettext_lazy("switch check signatures at each signature"), gettext_lazy("submit petition as ham"), gettext_lazy("submit petition as spam")]

        if petition.user:
            owner_type= "User"
            owner = petition.user.username
            owner_id = petition.user.user_id
        else:
            owner_type = "Organization"
            owner = petition.org.name
            owner_id = None

        context = dict(
            self.admin_site.each_context(request),
            petition=petition,
            text = clean_text_msg,
            mod_reason = mod_reason,
            mon_reason = mon_reason,
            actions = actions,
            owner_type = owner_type,
            owner = owner,
            owner_id = owner_id,
            actions_petition = actions_petition,
        )

        # Associate action names to the right functions
        if request.method == "POST":
            action_name = request.POST.get('action')
        
            if action_name == gettext_lazy("demonitor petition"):
                action_name = "monitor_element"

            elif action_name == gettext_lazy("moderate petition") or action_name == gettext_lazy("demoderate petition"):
                action_name = "moderate_element"

            elif action_name == gettext_lazy("delete petition"):
                action_name = "delete_element"   

            elif action_name == gettext_lazy("submit petition as ham"):
                action_name = "submit_ham"

            elif action_name == gettext_lazy("submit petition as spam"):
                action_name = "submit_spam"

            elif action_name == gettext_lazy("switch check signatures at each signature"):
                action_name = "check_periodically"

            if action_name in actions:
                func, _, _ = actions[action_name]
                response = func(self, request, queryset=Petition.objects.filter(pk=petition.pk))
            if response:
                return response 
            return HttpResponseRedirect(reverse('admin:moderatedelement_my_view'))


        return TemplateResponse(request, "admin/spam_petition.html", context)

    # custom view to display user detail when clicking on a user in the spam monitoring page
    def custom_user_detail(self, request, user):
        actions  = self.get_actions(request)
        mod_reason = None
        mon_reason = None

        # Get the moderation/monitoring status of the user and the associated actions to be displayed
        pytitionuser = PytitionUser.objects.get(user_id=user)

        actions_user = [gettext_lazy("moderate user"), gettext_lazy("delete user")]

        if pytitionuser.moderated:
            if pytitionuser.moderation.last().reason == None:
                mod_reason = gettext_lazy("not specified")
            else:
                mod_reason = pytitionuser.moderation.last().reason.text
            actions_user = [gettext_lazy("demoderate user"), gettext_lazy("delete user")]

        if pytitionuser.monitored:
            if pytitionuser.monitoring.last().reason == None:
                mon_reason = gettext_lazy("not specified")
            else:
                mon_reason = pytitionuser.monitoring.last().reason.text
            actions_user = [gettext_lazy("demonitor user"), gettext_lazy("moderate user"), gettext_lazy("delete user")]
        
        # Get the organizations that the user belongs to
        org = pytitionuser.organization_set.all()

        for orga in org:
            orga.num_petitions = orga.get_petition_number_org()
            orga.num_signatures = orga.get_total_signature_number()
        
        # Display the first n words of the user's petitions in the html table
        petition_queryset = pytitionuser.petition_set.all().order_by('-creation_date')
        n = 50

        for petition in petition_queryset:
            petition.num_signatures = petition.get_signature_number()

            soup = BeautifulSoup(petition.text, "html.parser")
            text_msg = soup.get_text(separator = " ")
            clean_text_msg = ' '.join(text_msg.split())
            cut_text_list = clean_text_msg.split()[:n]
            petition.cut_text_str = " ".join(cut_text_list)

        context = dict(
            self.admin_site.each_context(request),
            user=pytitionuser,
            name = pytitionuser.user.get_full_name(),
            num_petitions = pytitionuser.get_petition_number(),
            num_signatures = pytitionuser.get_total_signature_number(),
            orga = org,
            petitions = petition_queryset,
            mod_reason = mod_reason,
            mon_reason = mon_reason,
            actions_user = actions_user,
        )

        # Associate action names to the right functions
        if request.method == "POST":
            action_name = request.POST.get('action')
            if action_name == gettext_lazy("demoderate user") or action_name == gettext_lazy("moderate user"):
                action_name = "moderate_element"

            elif action_name == gettext_lazy("delete user"):
                action_name = "delete_element"   

            elif action_name == gettext_lazy("demonitor user"):
                action_name = "monitor_element"

            if action_name in actions:
                func, _, _ = actions[action_name]
                response = func(self, request, queryset=PytitionUser.objects.filter(pk=pytitionuser.pk))
            if response:
                return response 
            return HttpResponseRedirect(reverse('admin:moderatedelement_my_view'))
                
        return TemplateResponse(request, "admin/spam_user.html", context)

    # custom view to display organizatiob detail when clicking on an organization in the spam monitoring page
    def custom_org_detail(self, request, orga):
        actions  = self.get_actions(request)
        mod_reason = None
        mon_reason = None

        # Get the moderation/monitoring status of the organization and the associated actions to be displayed
        org = Organization.objects.get(name=orga)

        actions_org = [gettext_lazy("moderate organization"), gettext_lazy("delete organization")]

        if org.moderated:
            if org.moderation.last().reason == None:
                mod_reason = gettext_lazy("not specified")
            else:
                mod_reason = org.moderation.last().reason.text
            actions_org = [gettext_lazy("demoderate organization"), gettext_lazy("delete organization")]

        if org.monitored:
            if org.monitoring.last().reason == None:
                mon_reason = gettext_lazy("not specified")
            else:
                mon_reason = org.monitoring.last().reason.text
            actions_org = [gettext_lazy("demonitor organization"), gettext_lazy("moderate organization"), gettext_lazy("delete organization")]
       
       # Get the members of the organization
        members = org.members.all()

        for member in members:
            member.num_petitions = member.get_petition_number()
            member.num_signatures = member.get_total_signature_number()
        
        # display the first n words of the organization's petitions in the html table
        petition_queryset = org.petition_set.all().order_by('-creation_date')
        n = 50

        for petition in petition_queryset:
            petition.num_signatures = petition.get_signature_number()

            soup = BeautifulSoup(petition.text, "html.parser")
            text_msg = soup.get_text(separator = " ")
            clean_text_msg = ' '.join(text_msg.split())
            cut_text_list = clean_text_msg.split()[:n]
            petition.cut_text_str = " ".join(cut_text_list)

        context = dict(
            self.admin_site.each_context(request),
            org = org,
            members = members,
            petitions = petition_queryset,
            mod_reason = mod_reason,
            mon_reason = mon_reason,
            actions_org = actions_org,
        )

        # Associate action names to the right functions
        if request.method == "POST":
            action_name = request.POST.get('action')

            if action_name == gettext_lazy("demoderate organization") or action_name == gettext_lazy("moderate organization"):
                action_name = "moderate_element"

            elif action_name == gettext_lazy("delete organization"):
                action_name = "delete_element" 

            elif action_name == gettext_lazy("demonitor organization"):
                action_name = "monitor_element"  

            if action_name in actions:
                func, _, _ = actions[action_name]
                response = func(self, request, queryset=Organization.objects.filter(pk=org.pk))
            if response:
                return response 
            return HttpResponseRedirect(reverse('admin:moderatedelement_my_view'))
        
        return TemplateResponse(request, "admin/spam_org.html", context)
