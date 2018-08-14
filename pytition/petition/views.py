from django.shortcuts import render, redirect
from django.http import Http404, JsonResponse, HttpResponse
from django.core.mail import get_connection, send_mail
from django.core.mail.message import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.translation import ugettext as _

from .models import Petition, Signature

import requests
import csv


def settings_context_processor(request):
    return {'settings': settings}


def index(request):
    petition = Petition.objects.filter(published=True).latest('id')
    return redirect('/petition/{}'.format(petition.id))


def get_csv_signature(request, petition_id, only_confirmed):
    try:
        petition = Petition.objects.get(pk=petition_id)
    except Petition.DoesNotExist:
        raise Http404(_("This petition does not exist"))

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
    url = request.build_absolute_uri("/petition/confirm/{}/{}".format(petition.id, signature.confirmation_hash))
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
        data = petition.newsletter_subscribe_http_data
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
                         connection=connection).send(fail_silently=False)


def detail(request, petition_id, do_confirmation=False, confirmation_hash=None):
    try:
        petition = Petition.objects.get(pk=petition_id)
    except Petition.DoesNotExist:
        raise Http404(_("This petition does not exist"))

    if not petition.published and not request.user.is_authenticated:
        raise Http404(_("This Petition is not published yet!"))

    if request.method == "POST":
        post = request.POST
        firstname = post["first_name"]
        lastname = post["last_name"]
        email = post["email"]
        phone = post["phone_number"]
        try:
            emailOK = post["email_ok"]
            if emailOK == "Y":
                do_subscribe = True
            else:
                do_subscribe = False
        except:
            do_subscribe = False
        
        if not (firstname and lastname):
            errormsg = _("You must enter your first and last names for the signature to be valid.")
            return render(request, 'petition/detail2.html',
                          {'petition': petition, 'errormsg': errormsg, 'successmsg': None})
        
        try:
            validate_email(email)
        except ValidationError:
            errormsg = _("Invalid email address \'{email}\'").format(email=email)
            return render(request, 'petition/detail2.html',
                          {'petition': petition, 'errormsg': errormsg, 'successmsg': None})

        if petition.already_signed(email):
            return render(request, 'petition/detail2.html', {'petition': petition,
                                                             'errormsg': _('You already signed the petition.')})

        signature = petition.sign(firstname = firstname, lastname = lastname, email = email, phone = phone,
                                  subscribe = do_subscribe)
        send_confirmation_email(request, signature)
        successmsg = _("Thank you for signing this petition, an email has just been sent to you at your address \'{}\'" \
                       " in order to confirm your signature.<br>" \
                       "You will need to click on the confirmation link in the email.<br>" \
                       "If you cannot find the email in your Inbox, please have a look in your Spam box.").format(email)

        if do_subscribe and petition.has_newsletter:
            subscribe_to_newsletter(petition, email)

    else:
        if do_confirmation:
            successmsg = petition.confirm_signature(confirmation_hash)
            if successmsg is None:
                raise Http404(_("Error: This confirmation code is invalid. Maybe you\'ve already confirmed?"))
        else:
            successmsg = None

    return render(request, 'petition/detail2.html', {'petition': petition, 'errormsg': None, 'successmsg': successmsg})


def get_json_data(request, petition_id):
    petition = Petition.objects.get(pk=petition_id)
    signatures = petition.signature_set.filter(confirmed=True).all()
    return JsonResponse({"rows":[{"columns":[{"name":"participatingSupporters","value":len(signatures),"type":"xs:int","format":""}]}]})
