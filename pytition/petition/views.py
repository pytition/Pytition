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
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from .models import Petition, Signature, Organization, PytitionUser, PetitionTemplate, TemplateOwnership, Permission
from .forms import SignatureForm, PetitionTemplateForm

import requests
import csv


def get_session_user(request):
    try:
        pytitionuser = PytitionUser.objects.get(user__username=request.user.username)
    except User.DoesNotExist:
        raise Http404(_("not found"))
    return pytitionuser


def check_user_in_orga(user, orga):
    if orga not in user.organizations.all():
        return HttpResponseForbidden(_("You are not part of this organization"))
    return None


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

@login_required
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


@login_required
def org_dashboard(request, org_name):
    q = request.GET.get('q', '')

    try:
        org = Organization.objects.get(name=org_name)
    except Organization.DoesNotExist:
        raise Http404(_("not found"))

    pytitionuser = get_session_user(request)

    if org not in pytitionuser.organizations.all():
        return HttpResponseForbidden(_("You are not part of this organization."))

    if q != "":
        petitions = org.petitions.filter(Q(title__icontains=q) | Q(text__icontains=q))
    else:
        petitions = org.petitions


    other_orgs = pytitionuser.organizations.filter(~Q(name=org.name)).all()
    return render(request, 'petition/org_dashboard.html', {'org': org, 'user': pytitionuser, "other_orgs": other_orgs,
                                                           'petitions': petitions})

@login_required
def user_dashboard(request, user_name):
    try:
        user = PytitionUser.objects.get(user__username=user_name)
    except User.DoesNotExist:
        raise Http404(_("not found"))

    pytitionuser = get_session_user(request)

    if user.user != request.user:
        return HttpResponseForbidden(_("You are not allowed to view this users' dashboard"))

    q = request.GET.get('q', '')
    if q != "":
        petitions = user.petitions.filter(Q(title__icontains=q) | Q(text__icontains=q))
    else:
        petitions = user.petitions

    return render(request, 'petition/user_dashboard.html', {'user': pytitionuser, 'petitions': petitions})


@login_required
def user_profile(request, user_name):
    try:
        profile = PytitionUser.objects.get(user__username=user_name)
    except User.DoesNotExist:
        raise Http404(_("not found"))
    return render(request, 'petition/user_profile.html', {'profile': profile, 'user': request.user})


@login_required
def leave_org(request):
    org_name = request.GET.get('org', '')
    try:
        org = Organization.objects.get(name=org_name)
    except Organization.DoesNotExist:
        raise Http404(_("not found"))

    pytitionuser = get_session_user(request)

    if org not in pytitionuser.organizations.all():
        return JsonResponse({}, status=404)

    try:
        pytitionuser.organizations.remove(org)
    except:
        return JsonResponse({}, status=500)

    return JsonResponse({})


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


@login_required
def org_add_user(request, org_name):
    adduser = request.GET.get('user', '')

    try:
        adduser = PytitionUser.objects.get(user__username=adduser)
    except PytitionUser.DoesNotExist:
        message = _("This user does not exist (anylonger?)")
        return JsonResponse({"message": message}, status=404)

    try:
        org = Organization.objects.get(name=org_name)
    except Organization.DoesNotExist:
        message = _("This organization does not exist (anylonger?)")
        return JsonResponse({"message": message}, status=404)

    pytitionuser = get_session_user(request)

    if org not in pytitionuser.organizations.all():
        return HttpResponseForbidden(_("You are not part of this organization."))

    if org in adduser.organizations.all():
        message = _("User is already member of {orgname} organization".format(orgname=org.name))
        return JsonResponse({"message": message}, status=500)

    try:
        adduser.invitations.add(org)
        adduser.save()
    except:
        message = _("An error occured")
        return JsonResponse({"message": message}, status=500)

    message = _("You sent an invitation to join {orgname}".format(orgname=org.name))
    return JsonResponse({"message": message})


@login_required
def invite_accept(request):
    org_name = request.GET.get('org_name', '')

    if org_name == "":
        return JsonResponse({}, status=500)

    pytitionuser = get_session_user(request)

    try:
        org = Organization.objects.get(name=org_name)
    except Organization.DoesNotExist:
        return JsonResponse({}, status=404)

    if org in pytitionuser.invitations.all():
        try:
            pytitionuser.invitations.remove(org)
            pytitionuser.organizations.add(org)
            pytitionuser.save()
        except:
            return JsonResponse({}, status=500)

    return JsonResponse({})


@login_required()
def org_new_template(request, org_name):

    try:
        org = Organization.objects.get(name=org_name)
    except Organization.DoesNotExist:
        raise Http404(_("Organization does not exist"))

    pytitionuser = get_session_user(request)

    if org not in pytitionuser.organizations.all():
        return HttpResponseForbidden(_("You are not allowed to view this organization dashboard"))

    form = PetitionTemplateForm()
    return render(request, "petition/org_new_template.html", {'org': org, 'user': pytitionuser, 'form': form})


@login_required()
def edit_template(request):
    id = request.GET.get('id', '')

    if id == '':
        return HttpResponseForbidden(_("You need to provide the template id to modify"))

    try:
        template = PetitionTemplate.objects.get(pk=id)
    except PetitionTemplate.DoesNotExist:
        raise Http404(_("This template does not exist"))

    pytitionuser = get_session_user(request)
    context = {'user': pytitionuser}

    to = TemplateOwnership.objects.get(template=template)
    org_owner = to.organization
    user_owner = to.user

    if org_owner is not None:
        owner = org_owner
        owner_type = "org"
    elif user_owner is not None:
        owner = user_owner
        owner_type = "user"
    else:
        return HttpResponse(status=500)

    if org_owner is not None and user_owner is not None:
        return HttpResponse(status=500)

    if owner_type == "org":
        if owner not in pytitionuser.organizations.all():
            return HttpResponseForbidden(_("You are not allowed to edit this organization's templates"))
        context['org'] = owner
    elif owner_type == "user":
        if owner != pytitionuser:
            return HttpResponseForbidden(_("You are not allowed to edit this user's templates"))
    else:
        raise Http404(_("Cannot find template with unknown owner type \'{type}\'").format(type=owner_type))

    form = PetitionTemplateForm(instance=template)
    context['form'] = form
    return render(request, "petition/"+owner_type+"_new_template.html", context)


@login_required()
def user_new_template(request, user_name):

    pytitionuser = get_session_user(request)

    if pytitionuser.user != request.user:
        return HttpResponseForbidden(_("You are not allowed to create a template for this user"))

    form = PetitionTemplateForm()
    return render(request, "petition/user_new_template.html", {'user': pytitionuser, 'form': form})


@login_required()
def org_create_petition_template(request, org_name):

    try:
        org = Organization.objects.get(name=org_name)
    except Organization.DoesNotExist:
        raise Http404(_("Organization does not exist"))

    pytitionuser = get_session_user(request)

    if request.method == "POST":
        print("post: {}".format(request.POST))
        edit = request.POST['edit'] == '1'
        if edit:
            print("ON EDIT")
            pt = PetitionTemplate.objects.get(pk=request.POST['pk'])
            form = PetitionTemplateForm(data=request.POST, instance=pt)
        else:
            print("C EST DU NOUVEAU")
            form = PetitionTemplateForm(data=request.POST)
        if not form.is_valid():
            return render(request, 'petition/org_new_template.html', {'org': org, 'user': pytitionuser,
                                                                      'form': form})
        template = form.save()
        template.save()
        if not edit:
            to = TemplateOwnership(organization=org, template=template)
            to.save()
        messages.success(request, _("Hourra !"))
    else:
        form = PetitionTemplateForm()
        return render(request, "petition/org_new_template.html", {'user': pytitionuser, 'org': org, 'form': form})

    return redirect('org_dashboard', org_name)


@login_required()
def user_create_petition_template(request, user_name):

    try:
        pytitionuser = PytitionUser.objects.get(user__username=user_name)
    except PytitionUser.DoesNotExist:
        raise Http404(_("User does not exist"))

    if pytitionuser.user != request.user:
        return HttpResponseForbidden(_("You are not allowed to create templates for this user"))

    if request.method == "POST":
        form = PetitionTemplateForm(data=request.POST)
        if not form.is_valid():
            return render(request, 'petition/user_new_template.html', {'user': pytitionuser, 'form': form})
        template = form.save()
        template.save()
        to = TemplateOwnership(user=pytitionuser, template=template)
        to.save()
    else:
        form = PetitionTemplateForm()
        return render(request, "petition/user_new_template.html", {'user': pytitionuser, 'form': form})
    return redirect('user_dashboard', user_name)


@login_required()
def user_del_template(request, user_name):

    try:
        pytitionuser = PytitionUser.objects.get(user__username=user_name)
    except PytitionUser.DoesNotExist:
        raise Http404(_("User does not exist"))

    if pytitionuser.user != request.user:
        return HttpResponseForbidden(_("You are not allowed to delete this users' templates"))

    template = PetitionTemplate.objects.get(name=request.GET['name'])

    pytitionuser.petition_templates.remove(template)
    pytitionuser.save()

    return JsonResponse({})


@login_required()
def template_delete(request):
    id = request.GET.get('id', '')

    if id == '':
        return JsonResponse({}, status=500)

    pytitionuser = get_session_user(request)

    try:
        template = PetitionTemplate.objects.get(pk=id)
    except:
        return JsonResponse({}, status=404)

    try:
        templateOwnership = TemplateOwnership.objects.get(template=template)
    except:
        return JsonResponse({}, status=404)

    org_owner = templateOwnership.organization
    user_owner = templateOwnership.user

    if pytitionuser != user_owner and org_owner not in pytitionuser.organizations.all():
        return JsonResponse({}, status=403)  # User cannot delete a template if it's not his

    try:
        template.delete()
    except:
        return JsonResponse({}, status=500)

    return JsonResponse({})


@login_required()
def ptemplate_fav_toggle(request):
    id = request.GET.get('id', '')

    if id == '':
        return JsonResponse({}, status=500)

    try:
        template = PetitionTemplate.objects.get(pk=id)
    except PetitionTemplate.DoesNotExist:
        return JsonResponse({}, status=404)

    try:
        templateOwnership = TemplateOwnership.objects.get(template=template)
    except:
        return JsonResponse({}, status=404)

    pytitionuser = get_session_user(request)

    try:
        to = TemplateOwnership.objects.get(template=template)
    except TemplateOwnership.DoesNotExist:
        return JsonResponse({}, status=500)
    org_owner = to.organization
    user_owner = to.user

    if org_owner is not None:
        owner = org_owner
        owner_type = "org"
    elif user_owner is not None:
        owner = user_owner
        owner_type = "user"
    else:
        return HttpResponse(status=500)

    if org_owner is not None and user_owner is not None:
        return HttpResponse(status=500)

    if owner_type == "org":
        if owner not in pytitionuser.organizations.all():
            return JsonResponse({}, status=403)  # Forbidden
    elif owner_type =="user":
        if owner != pytitionuser:
            return JsonResponse({'msg': _("You are not allowed to change this user's default template")}, status=403)
    else:
        raise Http404(_("Cannot find template with unknown type \'{type}\'").format(type=type))

    if owner.default_template == template:
        owner.default_template = None
    else:
        owner.default_template = template
    owner.save()

    return JsonResponse({})


@login_required
def org_new_petition(request, org_name):

    try:
        org = Organization.objects.get(name=org_name)
    except Organization.DoesNotExist:
        raise Http404(_("Organization does not exist"))

    from petition.admin import PetitionAdmin
    pytitionuser = get_session_user(request)

    admin = PetitionAdmin(Petition, None)
    form = admin.get_form(request)

    return render(request, "petition/org_new_petition.html", {'org': org, 'user': pytitionuser, 'form': form})


@login_required
def org_create_petition(request, org_name):
    try:
        org = Organization.objects.get(name=org_name)
    except Organization.DoesNotExist:
        raise Http404(_("Organization does not exist"))


@login_required
def user_new_petition(request, user_name):
    try:
        pytitionuser = PytitionUser.objects.get(user__username=user_name)
    except PytitionUser.DoesNotExist:
        raise Http404(_("User does not exist"))

    if pytitionuser.user != request.user:
        return HttpResponseForbidden(_("You are not allowed to create petitions for this user"))

    from petition.admin import PetitionAdmin

    admin = PetitionAdmin(Petition, None)
    form = admin.get_form(request)

    return render(request, "petition/user_new_petition.html", {'user': pytitionuser, 'form': form})


@login_required
def user_create_petition(request, user_name):

    try:
        pytitionuser = PytitionUser.objects.get(user__username=user_name)
    except PytitionUser.DoesNotExist:
        raise Http404(_("User does not exist"))

    if pytitionuser.user != request.user:
        return HttpResponseForbidden(_("You are not allowed to create petitions for this user"))

@login_required
def org_delete_member(request, org_name):
    member_name = request.GET.get('member', '')
    try:
        member = PytitionUser.objects.get(user__username=member_name)
    except PytitionUser.DoesNotExist:
        raise Http404(_("User does not exist"))

    pytitionuser = get_session_user(request)

    try:
        org = Organization.objects.get(name=org_name)
    except Organization.DoesNotExist:
        raise Http404(_("Organization does not exist"))

    try:
        permissions = pytitionuser.permission.get(organization=org)
    except Permission.DoesNoeExist:
        return JsonResponse({}, status=500)

    if permissions.can_remove_members or pytitionuser == member:
        if org in member.organizations.all():
            member.organizations.remove(org)
        else:
            return JsonResponse({}, status=404)
    else:
        return JsonResponse({}, status=403)  # Forbidden

    return JsonResponse({}, status=200)