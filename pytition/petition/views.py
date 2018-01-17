from django.shortcuts import render, redirect
from django.http import Http404, JsonResponse, HttpResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

from .models import Petition, Signature

import uuid
import requests
import csv


def settings_context_processor(request):
    return {'settings': settings}


def index(request):
    petition = Petition.objects.latest('id')
    return redirect('/petition/{}'.format(petition.id))


def get_csv_signature(request, petition_id):
    try:
        petition = Petition.objects.get(pk=petition_id)
    except Petition.DoesNotExist:
        raise Http404("Petition does not exist")

    filename = '{}.csv'.format(petition)
    signatures = Signature.objects.filter(petition_id = petition_id).filter(confirmed = True).all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment;filename={}'.format(filename).replace('\r\n', '').replace(' ', '%20')
    writer = csv.writer(response)
    attrs = ['first_name', 'last_name', 'phone', 'email', 'subscribed_to_mailinglist']
    writer.writerow(attrs)
    for signature in signatures:
        values = [getattr(signature, field) for field in attrs]
        writer.writerow(values)
    return response


def detail(request, petition_id):
    try:
        petition = Petition.objects.get(pk=petition_id)
    except Petition.DoesNotExist:
        raise Http404("Petition does not exist")

    if request.method == "POST":
        post = request.POST
        firstname = post["first_name"]
        lastname = post["last_name"]
        email = post["email"]
        phone = post["phone_number"]
        try:
            emailOK = post["email_ok"]
            if emailOK == "Y":
                subscribe = True
            else:
                subscribe = False
        except:
            subscribe = False
        hash = str(uuid.uuid4())

        signatures = Signature.objects.filter(petition_id = petition_id)\
            .filter(confirmed = True).filter(email = email).all()
        if len(signatures) > 0:
            return render(request, 'petition/detail2.html', {'petition': petition,
                                                             'errormsg': 'Vous avez déjà signé la pétition'})

        signature = Signature.objects.create(first_name = firstname, last_name = lastname, email = email, phone = phone,
                                             petition_id = petition_id, confirmation_hash = hash,
                                             subscribed_to_mailinglist = subscribe)
        url = request.build_absolute_uri("/petition/confirm/{}".format(hash))
        html_message = render_to_string("petition/confirmation_email.html", {'firstname': firstname, 'url': url})
        message = strip_tags(html_message)
        send_mail("Confirmez votre signature à notre pétition", message, "petition@antipub.org", [email],
                  fail_silently=False, html_message=html_message)
        successmsg = "Merci d'avoir signé la pétition, vous allez recevoir un e-mail afin de confirmer votre signature.<br>" \
                     "Vous devrez cliquer sur le lien à l'intérieur du mail.<br>Si vous ne trouvez pas le mail consultez votre" \
                     "dossier \"spam\" ou \"indésirable\""

        if subscribe:
            if settings.NEWSLETTER_SUBSCRIBE_METHOD in ["POST", "GET"]:
                data = settings.NEWSLETTER_SUBSCRIBE_HTTP_DATA
                data[settings.NEWSLETTER_SUBSCRIBE_EMAIL_FIELDNAME] = email
            if settings.NEWSLETTER_SUBSCRIBE_METHOD == "POST":
                requests.post(settings.NEWSLETTER_SUBSCRIBE_URL, data)
            elif settings.NEWSLETTER_SUBSCRIBE_METHOD == "GET":
                requests.get(settings.NEWSLETTER_SUBSCRIBE_URL, data)
            elif settings.NEWSLETTER_SUBSCRIBE_METHOD == "MAIL":
                send_mail(settings.NEWSLETTER_SUBSCRIBE_MAIL_SUBJECT.format(email), "", "petition@antipub.org",
                          ["sympa@antipub.listes.vox.coop"], fail_silently=False)
            else:
                raise ValueError("setting NEWSLETTER_SUBSCRIBE_METHOD must either be POST or GET")
    else:
        successmsg = None

    return render(request, 'petition/detail2.html', {'petition': petition, 'errormsg': None, 'successmsg': successmsg})


def get_json_data(request, petition_id):
    petition = Petition.objects.get(pk=petition_id)
    signatures = petition.signature_set.filter(confirmed=True).all()
    return JsonResponse({"rows":[{"columns":[{"name":"participatingSupporters","value":len(signatures),"type":"xs:int","format":""}]}]})


def confirm(request, hash):
    signature = Signature.objects.get(confirmation_hash = hash)
    if signature:
        # Signature found, invalidating other signatures from same email
        email = signature.email
        Signature.objects.filter(email = email).exclude(confirmation_hash = hash).all().delete()
        # Now confirm the signature corresponding to this hash
        signature.confirmed = True
        signature.save()
        petition_id = signature.petition.id
        return redirect("/petition/{}".format(petition_id))
    else:
        raise Http404("Erreur: Cette confirmation n'existe pas")