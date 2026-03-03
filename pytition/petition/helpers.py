# -*- coding: utf-8 -*-
"""Helpers functions for pytition project

It defines actions to help the developper across the project.
"""

import requests
import lxml
from lxml.html.clean import Cleaner
from django.http import Http404, HttpResponseForbidden
from django.conf import settings
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import get_connection, EmailMultiAlternatives, EmailMessage
from django.utils.translation import gettext as _
from django.contrib.auth.models import User

# Remove all moderated instances of Petition
def remove_user_moderated(petitions):
    petitions = [p for p in petitions if not p.is_moderated]
    return petitions

# Remove all javascripts from HTML code
def sanitize_html(unsecure_html_content):
    cleaner = Cleaner(inline_style=False, scripts=True, javascript=True,
                      safe_attrs=lxml.html.defs.safe_attrs | set(['style', 'controls']),
                      frames=False, embedded=False,
                      meta=True, links=True, page_structure=True, remove_tags=['body'])
    try:
        cleaned = cleaner.clean_html(lxml.html.fromstring(unsecure_html_content))

        for p in cleaned.xpath('//p[video]'):
            p.drop_tag()

        secure_html_content = lxml.html.tostring(cleaned, method="html")
    except:
        secure_html_content = b''
    return secure_html_content.decode()

# Get the client IP address, considering proxies and RP
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# Get the user of the current session
def get_session_user(request):
    from .models import PytitionUser
    try:
        pytitionuser = PytitionUser.objects.get(user__username=request.user.username)
    except User.DoesNotExist:
        raise Http404(_("not found"))
    return pytitionuser

# Check if an user is in an organization
# FIXME : move this as an org method ?
def check_user_in_orga(user, orga):
    if orga not in user.organizations.all():
        return HttpResponseForbidden(_("You are not part of this organization"))
    return None


# Return a 404 if a petition does not exist
def petition_from_id(id):
    from .models import Petition
    petition = Petition.by_id(id)
    if petition is None:
        raise Http404(_("Petition does not exist"))
    else:
        return petition


# Check if a petition is publicly accessible
def check_petition_is_accessible(request, petition):
    if petition.published and not petition.moderated:
        return True
    if request.user.is_authenticated:
        user = get_session_user(request)
        if petition.owner_type == "user" and user == petition.owner:
            return True
        if petition.owner_type == "org" and user in petition.owner.members.all():
            return True
    if petition.moderated:
        raise Http404(_("This Petition has been moderated!"))
    if not petition.published:
        raise Http404(_("This Petition is not published yet!"))


# Get settings
def settings_context_processor(request):
    return {'settings': settings}

# Get footer content
def footer_content_processor(request):
    footer_content = None
    if settings.FOOTER_TEMPLATE:
        footer_content = render_to_string(settings.FOOTER_TEMPLATE)
    return {'footer_content': footer_content}

# Send Confirmation email
def send_confirmation_email(request, signature):
    petition = signature.petition
    url = request.build_absolute_uri(reverse("confirm", args=[petition.id, signature.confirmation_hash]))
    message = render_to_string("petition/confirmation_email.txt", {'firstname': signature.first_name, 'confirmation_url': url, 'petition': petition, 'petition_url': request.build_absolute_uri(petition.get_absolute_url())})
    html_message = render_to_string("petition/confirmation_email.html", {'firstname': signature.first_name, 'confirmation_url': url, 'petition': petition, 'petition_url': request.build_absolute_uri(petition.get_absolute_url())})
    with get_connection() as connection:
        msg = EmailMultiAlternatives(_("Confirm your signature to our petition"),
                           message, to=[signature.email], connection=connection,
                           reply_to=[petition.confirmation_email_reply])
        msg.attach_alternative(html_message, "text/html")
        msg.send(fail_silently=False)

# Send welcome mail on account creation
def send_welcome_mail(user_infos):
    message = render_to_string("registration/confirmation_email.txt", {'firstname': user_infos["first_name"], 'username': user_infos["username"], 'login_url': settings.SITE_URL + reverse('login'), 'site_name': settings.SITE_NAME})
    html_message = render_to_string("registration/confirmation_email.html", {'firstname': user_infos["first_name"], 'username': user_infos["username"], 'login_url': settings.SITE_URL + reverse('login'), 'site_name': settings.SITE_NAME})
    with get_connection() as connection:
        msg = EmailMultiAlternatives(_("Account created on %(site_name)s!") % {'site_name': settings.SITE_NAME},
                                     message, to=[user_infos["email"]], connection=connection,
                                     reply_to=[settings.DEFAULT_NOREPLY_MAIL])
        msg.attach_alternative(html_message, "text/html")
        msg.send(fail_silently=False)


# Send moderation mail to user
def send_moderation_mail(email, username, reason, element_type, element):
    message = render_to_string("admin/emails/moderation_email.txt", {'username': username, 'reason': reason, 'element_type': element_type, 'element': element})
    html_message = render_to_string("admin/emails/moderation_email.html", {'username': username, 'reason': reason, 'element_type': element_type, 'element': element})
    with get_connection() as connection:
        msg = EmailMultiAlternatives(_("%(site_name)s: your petition has been moderated") % {'site_name': settings.SITE_NAME},
                                     message, to=[email], connection=connection,
                                     reply_to=[settings.DEFAULT_NOREPLY_MAIL])
        msg.attach_alternative(html_message, "text/html")
        msg.send(fail_silently=False)

# Send monitoring mail to user
def send_monitoring_mail(email, username, element_type, element, reason):
    if settings.SEND_MONITORING_MAIL_TO_USER:
        message = render_to_string("admin/emails/monitoring_email.txt", {'username': username, 'reason': reason, 'element_type': element_type, 'element': element, 'site_url': settings.SITE_URL})
        html_message = render_to_string("admin/emails/monitoring_email.html", {'username': username, 'reason': reason, 'element_type': element_type, 'element': element, 'site_url': settings.SITE_URL})
        with get_connection() as connection:
            msg = EmailMultiAlternatives(_("%(site_name)s: your petition has been monitered") % {'site_name': settings.SITE_NAME},
                                         message, to=[email], connection=connection,
                                         reply_to=[settings.DEFAULT_NOREPLY_MAIL])
            msg.attach_alternative(html_message, "text/html")
            msg.send(fail_silently=False)

# Send mail to moderation about moderation
def send_mail_to_moderation(moderation_email, element, reason, owner_type):
    message = render_to_string("admin/emails/email_to_moderation.txt", {'element': element, 'reason': reason, 'owner_type': owner_type, 'site_url': settings.SITE_URL, 'admin_moderation_url': settings.SITE_URL + reverse('admin:moderatedelement_my_view')})
    html_message = render_to_string("admin/emails/email_to_moderation.html", {'element': element, 'reason': reason, 'owner_type': owner_type, 'site_url': settings.SITE_URL, 'admin_moderation_url': settings.SITE_URL + reverse('admin:moderatedelement_my_view')})
    with get_connection() as connection:
        msg = EmailMultiAlternatives(_("New petition moderated"),
                                     message, to=[moderation_email], connection=connection,
                                     reply_to=[settings.DEFAULT_NOREPLY_MAIL])
        msg.attach_alternative(html_message, "text/html")
        msg.send(fail_silently=False)

# Send mail to moderation about monitoring
def send_mail_to_moderation_monitor(moderation_email, element, reason, owner_type, priority):
    message = render_to_string("admin/emails/email_to_moderation_monitor.txt", {'element': element, 'reason': reason, 'owner_type': owner_type, 'site_url': settings.SITE_URL, 'admin_moderation_url': settings.SITE_URL + reverse('admin:moderatedelement_my_view') + "#monitoredPetitions"})
    html_message = render_to_string("admin/emails/email_to_moderation_monitor.html", {'element': element, 'reason': reason, 'owner_type': owner_type, 'site_url': settings.SITE_URL, 'admin_moderation_url': settings.SITE_URL + reverse('admin:moderatedelement_my_view') + "#monitoredPetitions"})
    with get_connection() as connection:
        msg = EmailMultiAlternatives(_("New petition monitored"),
                                     message, to=[moderation_email], connection=connection,
                                     reply_to=[settings.DEFAULT_NOREPLY_MAIL])
        msg.attach_alternative(html_message, "text/html")
        msg.send(fail_silently=False)        

# Send mail to moderation with information eg Akismet is down
def send_mail_to_moderation_info(moderation_email, info):
    message = render_to_string("admin/emails/email_to_moderation_info.txt", {'info': info})
    html_message = render_to_string("admin/emails/email_to_moderation_info.html", {'info': info})
    with get_connection() as connection:
        msg = EmailMultiAlternatives(_("Information"),
                                     message, to=[moderation_email], connection=connection,
                                     reply_to=[settings.DEFAULT_NOREPLY_MAIL])
        msg.attach_alternative(html_message, "text/html")
        msg.send(fail_silently=False)

# Send mail to moderation when a report is made
def send_mail_to_moderation_report(moderation_email, request, petition, reason = None):
    message = render_to_string("admin/emails/email_to_moderation_report.txt", {'petition': petition, 'reason': reason, 'petition_url': request.build_absolute_uri(petition.get_absolute_url()), 'admin_moderation_url': request.build_absolute_uri(reverse('admin:moderatedelement_my_view') + "#reportedPetitions") })
    html_message = render_to_string("admin/emails/email_to_moderation_report.html", {'petition': petition, 'reason': reason, 'petition_url': request.build_absolute_uri(petition.get_absolute_url()), 'admin_moderation_url': request.build_absolute_uri(reverse('admin:moderatedelement_my_view') + "#reportedPetitions") })
    with get_connection() as connection:
        msg = EmailMultiAlternatives(_("New petition reported"),
                                     message, to=[moderation_email], connection=connection,
                                     reply_to=[settings.DEFAULT_NOREPLY_MAIL])
        msg.attach_alternative(html_message, "text/html")
        msg.send(fail_silently=False)


# Generate a meta url for the HTML meta property
def petition_detail_meta(request, petition_id):
    url = "{scheme}://{host}{petition_path}".format(
        scheme=request.scheme,
        host=request.get_host(),
        petition_path=reverse('detail', args=[petition_id]))
    return {'site_url': request.get_host(), 'petition_url': url}


def subscribe_to_newsletter(petition, email):
    if petition.newsletter_subscribe_method in ["POST", "GET"]:
        if petition.newsletter_subscribe_http_url == '':
            return
        data = petition.newsletter_subscribe_http_data
        if data == '' or data is None:
            data = {}
        else:
            import json
            data = data.replace("'", "\"")
            data = json.loads(data)
        if petition.newsletter_subscribe_http_mailfield != '':
            data[petition.newsletter_subscribe_http_mailfield] = email
    if petition.newsletter_subscribe_method == "POST":
        requests.post(petition.newsletter_subscribe_http_url, data)
    elif petition.newsletter_subscribe_method == "GET":
        requests.get(petition.newsletter_subscribe_http_url, data)
    elif petition.newsletter_subscribe_method == "MAIL":
        with get_connection(host=petition.newsletter_subscribe_mail_smtp_host,
                            port=petition.newsletter_subscribe_mail_smtp_port,
                            username=petition.newsletter_subscribe_mail_smtp_user,
                            password=petition.newsletter_subscribe_mail_smtp_password,
                            use_ssl=petition.newsletter_subscribe_mail_smtp_tls,
                            use_tls=petition.newsletter_subscribe_mail_smtp_starttls) as connection:
            EmailMessage(petition.newsletter_subscribe_mail_subject.format(email), "",
                         petition.newsletter_subscribe_mail_from, [petition.newsletter_subscribe_mail_to],
                         connection=connection).send(fail_silently=True)

def get_update_form(user, data=None):
    from .forms import UpdateInfoForm
    if not data:
        _data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email
        }
    else:
        _data = data
    return UpdateInfoForm(user, _data)
