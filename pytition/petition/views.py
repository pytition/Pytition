from django.shortcuts import render, redirect
from django.http import Http404, JsonResponse
from django.core.mail import send_mail

from .models import Petition, Signature

import uuid

def index(request):
    pass


def detail(request, petition_id):
    try:
        petition = Petition.objects.get(pk=petition_id)
    except Petition.DoesNotExist:
        raise Http404("Petition does not exist")
    return render(request, 'petition/detail2.html', {'petition': petition})


def vote(request, petition_id):
    if request.method == "POST":
        post = request.POST
        firstname = post["first_name"]
        lastname = post["last_name"]
        email = post["email"]
        phone = post["phone_number"]
        hash = str(uuid.uuid4())

        signatures = Signature.objects.filter(petition_id = petition_id).filter(confirmed = True).filter(email = email).all()
        if len(signatures) > 0:
            raise Http404("Vous avez déjà signé la pétition")

        signature = Signature.objects.create(first_name = firstname, last_name = lastname, email = email, phone = phone,
                                             petition_id = petition_id, confirmation_hash = hash)
        send_mail("Confirmez votre signature à notre pétition", "Bravo, veuillez cliquer <a href=\"http://127.0.0.1/petition/confirm/{}\">ici</a>".format(hash), "petition@antipub.org", [email], fail_silently=False)
        return redirect("/petition/{}".format(petition_id))
    else:
        raise Http404("no GET method for this URI")


def get_json_data(request, petition_id):
    petition = Petition.objects.get(pk=petition_id)
    signatures = petition.signature_set.filter(confirmed=True).all()
    return JsonResponse({"rows":[{"columns":[{"name":"participatingSupporters","value":len(signatures),"type":"xs:int","format":""}]}]})


def confirm(request, hash):
    signature = Signature.objects.get(confirmation_hash = hash)
    if signature:
        signature.confirmed = True
        signature.save()
        petition_id = signature.petition.id
        return redirect("/petition/{}".format(petition_id))
    else:
        raise Http404("Erreur: Cette confirmation n'existe pas")