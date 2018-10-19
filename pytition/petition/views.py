from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse, HttpResponseForbidden, JsonResponse
from django.core.mail import get_connection, send_mail
from django.core.mail.message import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.utils.html import format_html
from django.db.models import Q

from django.contrib.auth.models import User
from .models import Petition, Signature, Organization, PytitionUser
from .forms import SignatureForm

import requests
import csv


def petition_from_id(id):
    petition = Petition.by_id(id)
    if petition is None:
        raise Http404(_("Petition does not exist"))
    else:
        return petition


def check_petition_is_accessible(request, petition):
    if not petition.published and not request.user.is_authenticated:
        raise Http404(_("This Petition is not published yet!"))


def settings_context_processor(request):
    return {'settings': settings}


def index(request):
    authenticated = request.user.is_authenticated
    q = request.GET.get('q', '')
    if q != "":
        petitions = Petition.objects.filter(Q(title__icontains=q) | Q(text__icontains=q)).filter(published=True)
    else:
        petitions = Petition.objects.filter(published=True)
    title = "Pétitions Résistance à l'agression publicitaire"
    return render(request, 'petition/index.html', {'petitions': petitions, 'title': title,
                                                   'authenticated': authenticated, 'q': q})


def get_csv_signature(request, petition_id, only_confirmed):
    petition = petition_from_id(petition_id)

    filename = '{}.csv'.format(petition)
    signatures = Signature.objects.filter(petition_id = petition_id)
    if only_confirmed:
        signatures = signatures.filter(confirmed = True)
    signatures = signatures.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment;filename={}'.format(filename).replace('\r\n', '').replace(' ', '%20')
    writer = csv.writer(response)
    attrs = ['first_name', 'last_name', 'phone', 'email', 'subscribed_to_mailinglist', 'confirmed']
    writer.writerow(attrs)
    for signature in signatures:
        values = [getattr(signature, field) for field in attrs]
        writer.writerow(values)
    return response


def send_confirmation_email(request, signature):
    petition = signature.petition
    url = request.build_absolute_uri("/petition/{}/confirm/{}".format(petition.id, signature.confirmation_hash))
    html_message = render_to_string("petition/confirmation_email.html", {'firstname': signature.first_name, 'url': url})
    message = strip_tags(html_message)
    with get_connection(host=petition.confirmation_email_smtp_host, port=petition.confirmation_email_smtp_port,
                        username=petition.confirmation_email_smtp_user,
                        password=petition.confirmation_email_smtp_password,
                        use_ssl=petition.confirmation_email_smtp_tls,
                        use_tls=petition.confirmation_email_smtp_starttls) as connection:
        send_mail(_("Confirm your signature to our petition"), message, petition.confirmation_email_sender,
                     [signature.email], html_message=html_message, connection=connection, fail_silently=False)


def go_send_confirmation_email(request, signature_id):
    app_label = Signature._meta.app_label
    signature = Signature.objects.filter(pk=signature_id).get()
    send_confirmation_email(request, signature)
    return redirect(reverse('admin:{}_signature_change'.format(app_label), args=[signature_id]))


def subscribe_to_newsletter(petition, email):
    if petition.newsletter_subscribe_method in ["POST", "GET"]:
        if petition.newsletter_subscribe_http_url == '':
            return
        data = petition.newsletter_subscribe_http_data
        if data == '' or data is None:
            data = {}
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


def create_signature(request, petition_id):
    petition = petition_from_id(petition_id)
    check_petition_is_accessible(request, petition)

    if request.method == "POST":
        form = SignatureForm(petition=petition, data=request.POST)
        if not form.is_valid():
            return render(request, 'petition/detail2.html', {'petition': petition, 'form': form})

        signature = form.save()
        send_confirmation_email(request, signature)
        messages.success(request,
            format_html(_("Thank you for signing this petition, an email has just been sent to you at your address \'{}\'" \
            " in order to confirm your signature.<br>" \
            "You will need to click on the confirmation link in the email.<br>" \
            "If you cannot find the email in your Inbox, please have a look in your Spam box.")\
            , signature.email))

        if petition.has_newsletter and signature.subscribed_to_mailinglist:
            subscribe_to_newsletter(petition, signature.email)

    return redirect('/petition/{}'.format(petition.id))


def confirm(request, petition_id, confirmation_hash):
    petition = petition_from_id(petition_id)
    check_petition_is_accessible(request, petition)

    try:
        successmsg = petition.confirm_signature(confirmation_hash)
        if successmsg is None:
            messages.error(request, _("Error: This confirmation code is invalid. Maybe you\'ve already confirmed?"))
        else:
            messages.success(request, successmsg)
    except ValidationError as e:
        messages.error(request, _(e.message))
    except Signature.DoesNotExist:
        messages.error(request, _("Error: This confirmation code is invalid."))
    return redirect('/petition/{}'.format(petition.id))


def detail(request, petition_id):
    petition = petition_from_id(petition_id)
    check_petition_is_accessible(request, petition)
    sign_form = SignatureForm(petition=petition)
    return render(request, 'petition/detail2.html', {'petition': petition, 'form': sign_form})


def org_dashboard(request, org_name):
    if not request.user.is_authenticated:
        raise HttpResponseForbidden(_("You must log-in first"))
    try:
        org = Organization.objects.get(name=org_name)
    except Organization.DoesNotExist:
        raise Http404(_("not found"))

    try:
        pytitionuser = PytitionUser.objects.get(user__username=request.user.username)
    except User.DoesNotExist:
        raise Http404(_("not found"))

    other_orgs = pytitionuser.organizations.filter(~Q(name=org.name))
    return render(request, 'petition/org_dashboard.html', {'org': org, 'user': request.user, "other_orgs": other_orgs})


def user_dashboard(request, user_name):
    if not request.user.is_authenticated:
        raise HttpResponseForbidden(_("You must log-in first"))
    try:
        pytitionuser = PytitionUser.objects.get(user__username=request.user.username)
    except User.DoesNotExist:
        raise Http404(_("not found"))
    return render(request, 'petition/user_dashboard.html', {'pytitionuser': pytitionuser})


def user_profile(request, user_name):
    try:
        profile = PytitionUser.objects.get(user__username=user_name)
    except User.DoesNotExist:
        raise Http404(_("not found"))
    return render(request, 'petition/user_profile.html', {'profile': profile, 'user': request.user})


def leave_org(request, org_name):
    try:
        org = Organization.objects.get(name=org_name)
    except Organization.DoesNotExist:
        raise Http404(_("not found"))

    if not request.user.is_authenticated:
        raise HttpResponseForbidden(_("You must log-in first"))

    try:
        pytitionuser = PytitionUser.objects.get(user__username=request.user.username)
    except User.DoesNotExist:
        raise Http404(_("not found"))

    try:
        pytitionuser.organizations.remove(org)
    except:
        raise Http404(_("not found"))

    return redirect('/petition/user/{name}/dashboard'.format(name=pytitionuser.user.username))


def org_profile(request, org_name):
    pass

def get_user_list(request):
    q = request.GET.get('q', '')
    if q != "":
        users = PytitionUser.objects.filter(Q(user__username__contains=q) | Q(user__first_name__icontains=q) |
                                            Q(user__last_name__icontains=q)).all()
    else:
        users =  []

    userdict = {
        "values": [user.user.username for user in users],
    }
    return JsonResponse(userdict)

def org_add_user(request, org_name):
    user = request.GET.get('user', '')
    print("on rajoute {}".format(user))

    if user != "":
        users = PytitionUser.objects.get(user__username=user)

    if users is None:
        return JsonResponse({"status": "KO"})
    else:
        return JsonResponse({"status": "OK"})