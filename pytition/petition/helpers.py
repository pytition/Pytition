import requests
import lxml
from lxml.html.clean import Cleaner
from django.http import Http404, HttpResponseForbidden
from django.conf import settings
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import get_connection, EmailMultiAlternatives, EmailMessage
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User


# Remove all javascripts from HTML code
def sanitize_html(unsecure_html_content):
    cleaner = Cleaner(inline_style=False, scripts=True, javascript=True,
                      safe_attrs=lxml.html.defs.safe_attrs | set(['style']),
                      frames=False, embedded=False,
                      meta=True, links=True, page_structure=True)
    try:
        secure_html_content = lxml.html.tostring(cleaner.clean_html(lxml.html.fromstring(unsecure_html_content)), method="html")
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
    if not petition.published and not request.user.is_authenticated:
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
    url = request.build_absolute_uri("/petition/{}/confirm/{}".format(petition.id, signature.confirmation_hash))
    html_message = render_to_string("petition/confirmation_email.html", {'firstname': signature.first_name, 'url': url})
    message = strip_tags(html_message)
    with get_connection() as connection:
        msg = EmailMultiAlternatives(_("Confirm your signature to our petition"),
                           message, to=[signature.email], connection=connection,
                           reply_to=[petition.confirmation_email_reply])
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
