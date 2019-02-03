from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse, HttpResponseForbidden, JsonResponse
from django.core.mail import get_connection, send_mail
from django.core.mail.message import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.core.exceptions import ValidationError
from django.urls import reverse, reverse_lazy
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.utils.html import format_html
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth.models import User
from .models import Petition, Signature, Organization, PytitionUser, PetitionTemplate, TemplateOwnership, Permission
from .forms import SignatureForm, PetitionTemplateForm, ContentForm, EmailForm, NewsletterForm, SocialNetworkForm

from formtools.wizard.views import SessionWizardView

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

    try:
        permissions = pytitionuser.permissions.get(organization=org)
    except:
        return HttpResponse(
            _("Internal error, cannot find your permissions attached to this organization (\'{orgname}\')"
              .format(orgname=org.name)), status=500)

    other_orgs = pytitionuser.organizations.filter(~Q(name=org.name)).all()
    return render(request, 'petition/org_dashboard.html', {'org': org, 'user': pytitionuser, "other_orgs": other_orgs,
                                                           'petitions': petitions, 'user_permissions': permissions})

@login_required
def user_dashboard(request):
    user = get_session_user(request)

    q = request.GET.get('q', '')
    if q != "":
        petitions = user.petitions.filter(Q(title__icontains=q) | Q(text__icontains=q))
    else:
        petitions = user.petitions

    return render(request, 'petition/user_dashboard.html', {'user': user, 'petitions': petitions})


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


@login_required
def org_profile(request, org_name):
    pass


@login_required
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
        permissions = pytitionuser.permissions.get(organization=org)
    except:
        message = _("Internal error, cannot find your permissions attached to this organization (\'{orgname}\')".
                    format(orgname=org.name))
        return JsonResponse({"message": message}, status=500)

    if not permissions.can_add_members:
        message = _("You are not allowed to invite new members into this organization.")
        return JsonResponse({"message": message}, status=403)

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
            with transaction.atomic():
                pytitionuser.invitations.remove(org)
                org.add_member(pytitionuser)
        except:
            return JsonResponse({}, status=500)
    else:
        return JsonResponse({}, status=404)

    return JsonResponse({})

@login_required
def invite_dismiss(request):
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
        except:
            return JsonResponse({}, status=500)
    else:
        return JsonResponse({}, status=404)

    return JsonResponse({})


@login_required
def org_new_template(request, org_name):

    try:
        org = Organization.objects.get(name=org_name)
    except Organization.DoesNotExist:
        raise Http404(_("Organization does not exist"))

    pytitionuser = get_session_user(request)

    if org not in pytitionuser.organizations.all():
        return HttpResponseForbidden(_("You are not allowed to view this organization dashboard"))

    try:
        permissions = pytitionuser.permissions.get(organization=org)
    except:
        return HttpResponse(
            _("Internal error, cannot find your permissions attached to this organization (\'{orgname}\')"
              .format(orgname=org_name)), status=500)

    form = PetitionTemplateForm()
    return render(request, "petition/org_new_template.html", {'org': org, 'user': pytitionuser, 'form': form,
                                                              'user_permissions': permissions})


@login_required
def edit_template(request, template_id):
    id = template_id
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
        try:
            permissions = pytitionuser.permissions.get(organization=owner)
        except:
            return HttpResponse(
                _("Internal error, cannot find your permissions attached to this organization (\'{orgname}\')"
                  .format(orgname=owner.name)), status=500)
        context['user_permissions'] = permissions
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


@login_required
def user_new_template(request, user_name):

    pytitionuser = get_session_user(request)

    if pytitionuser.user != request.user:
        return HttpResponseForbidden(_("You are not allowed to create a template for this user"))

    form = PetitionTemplateForm()
    return render(request, "petition/user_new_template.html", {'user': pytitionuser, 'form': form})


@login_required
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


@login_required
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
    return redirect('user_dashboard')


@login_required
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


@login_required
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


@login_required
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
        permissions = pytitionuser.permissions.get(organization=org)
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


@login_required
def org_edit_user_perms(request, org_name, user_name):
    """Shows the page which lists the user permissions."""
    pytitionuser = get_session_user(request)

    try:
        member = PytitionUser.objects.get(user__username=user_name)
    except PytitionUser.DoesNotExist:
        messages.error(request, _("User '{name}' does not exist".format(name=user_name)))
        return redirect(reverse("org_dashboard", args=[org_name]))

    try:
        org = Organization.objects.get(name=org_name)
    except Organization.DoesNotExist:
        raise Http404(_("Organization '{name}' does not exist".format(name=org_name)))

    if org not in member.organizations.all():
        messages.error(request, _("The user '{username}' is not member of this organization ({orgname}).".
                                  format(username=user_name, orgname=org_name)))
        return redirect(reverse("org_dashboard", args=[org_name]))

    try:
        permissions = member.permissions.get(organization=org)
    except Permission.DoesNotExist:
        messages.error(request,
                       _("Internal error, this member does not have permissions attached to this organization."))
        return redirect(reverse("org_dashboard", args=[org_name]))

    try:
        user_permissions = pytitionuser.permissions.get(organization=org)
    except:
        return HttpResponse(
            _("Internal error, cannot find your permissions attached to this organization (\'{orgname}\')"
              .format(orgname=org.name)), status=500)

    return render(request, "petition/org_edit_user_perms.html", {'org': org, 'member': member, 'user': pytitionuser,
                                                                 'permissions': permissions,
                                                                 'user_permissions': user_permissions})

@login_required
def org_set_user_perms(request, org_name, user_name):
    """Actually do the modification of user permissions.
    Data come from "org_edit_user_perms" view's form.
    """

    pytitionuser = get_session_user(request)

    try:
        member = PytitionUser.objects.get(user__username=user_name)
    except PytitionUser.DoesNotExist:
        messages.error(request, _("User does not exist"))
        return redirect(reverse("org_dashboard", args=[org_name]))
        #raise Http404(_("User does not exist"))

    try:
        org = Organization.objects.get(name=org_name)
    except Organization.DoesNotExist:
        raise Http404(_("Organization does not exist"))

    if org not in member.organizations.all():
        messages.error(request, _("This user is not part of organization \'{orgname}\'".format(orgname=org.name)))
        return redirect(reverse("org_dashboard", args=[org_name]))

    try:
        permissions = member.permissions.get(organization=org)
    except Permission.DoesNotExist:
        messages.error(request, _("PLOP"));
        return redirect(reverse("org_dashboard", args=[org_name]))

    try:
        userperms = pytitionuser.permissions.get(organization=org)
    except:
        messages.error(request, _("PLAP"));
        return redirect(reverse("org_dashboard", args=[org_name]))

    if request.method == "POST":
        if not userperms.can_modify_permissions:
            messages.error(request, _("You are not allowed to modify this organization members' permissions"))
        else:
            post = request.POST
            permissions.can_remove_members = post.get('can_remove_members', '') == 'on'
            permissions.can_add_members = post.get('can_add_members', '') == 'on'
            permissions.can_create_petitions = post.get('can_create_petitions', '') == 'on'
            permissions.can_modify_petitions = post.get('can_modify_petitions', '') == 'on'
            permissions.can_delete_petitions = post.get('can_delete_petitions', '') == 'on'
            permissions.can_view_signatures = post.get('can_view_signatures', '') == 'on'
            permissions.can_modify_signatures = post.get('can_modify_signatures', '') == 'on'
            permissions.can_delete_signatures = post.get('can_delete_signatures', '') == 'on'
            permissions.can_modify_permissions = post.get('can_modify_permissions', '') == 'on'
            permissions.save()
            messages.success(request, _("Permissions successfully changed!"))
    return redirect(reverse("org_edit_user_perms", args=[org_name, user_name]))

from .forms import PetitionCreationStep1, PetitionCreationStep2, PetitionCreationStep3

WizardTemplates = {"step1": "petition/new_petition_step1.html",
                    "step2": "petition/new_petition_step2.html",
                    "step3": "petition/new_petition_step3.html"}

WizardForms = [("step1", PetitionCreationStep1),
         ("step2", PetitionCreationStep2),
         ("step3", PetitionCreationStep3)]


# FIXME: add equivalent of @login_required here
class PetitionCreationWizard(SessionWizardView):
    def get_template_names(self):
        print("step: {}".format(self.steps.current))
        return [WizardTemplates[self.steps.current]]

    def done(self, form_list, **kwargs):
        org_petition = "org_name" in self.kwargs
        title = self.get_cleaned_data_for_step("step1")["title"]
        message = self.get_cleaned_data_for_step("step2")["message"]
        pytitionuser = get_session_user(self.request)

        if org_petition:
            org_name = self.kwargs['org_name']
            try:
                org = Organization.objects.get(name=self.kwargs['org_name'])
            except Organization.DoesNotExist:
                raise Http404(_("Organization does not exist"))

            try:
                permissions = pytitionuser.permissions.get(organization=org)
            except Permission.DoesNotExist:
                return redirect(reverse("org_dashboard", args=[org_name]))

            if pytitionuser in org.members.all() and permissions.can_create_petitions:
                petition = Petition.objects.create(title=title, text=message)
                org.petitions.add(petition)
                petition.save()
                return redirect(reverse("org_dashboard", args=[org_name]))
        else:
            petition = Petition.objects.create(title=title, text=message)
            pytitionuser.petitions.add(petition)
            petition.save()
            return redirect(reverse("user_dashboard"))

    def get_context_data(self, form, **kwargs):
        org_petition = "org_name" in self.kwargs
        context = super(PetitionCreationWizard, self).get_context_data(form=form, **kwargs)
        if org_petition:
            base_template = 'petition/org_base.html'
            try:
                org = Organization.objects.get(name=self.kwargs['org_name'])
            except Organization.DoesNotExist:
                raise Http404(_("Organization does not exist"))
        else:
            base_template = 'petition/user_base.html'

        pytitionuser = get_session_user(self.request)
        context.update({'user': pytitionuser,
                        'base_template': base_template})

        if org_petition:
            try:
                permissions = pytitionuser.permissions.get(organization=org)
            except:
                return HttpResponse(
                    _("Internal error, cannot find your permissions attached to this organization (\'{orgname}\')"
                      .format(orgname=org.name)), status=500)
            context.update({'org': org,
                            'user_permissions': permissions})

        if self.steps.current == "step3":
            context.update(self.get_cleaned_data_for_step("step1"))
            context.update(self.get_cleaned_data_for_step("step2"))
        return context


@login_required
def petition_delete(request):
    petition_id = request.GET.get('id', '')
    petition = petition_from_id(petition_id)
    pytitionuser = get_session_user(request)

    if petition in pytitionuser.petitions.all():
        print("La pétition appartient bien à cet utilisateur {}".format(pytitionuser))
        petition.delete()
        return JsonResponse({})
    else:
        for org in pytitionuser.organizations.all():
            if petition in org.petitions.all():
                print("La pétition appartient à l'orga {orga} dont l'utilisateur {user} est bien membre"
                      .format(orga=org, user=pytitionuser))
                userperms = pytitionuser.permissions.get(organization=org)
                if userperms.can_delete_petitions:
                    print("L'utilisateur {user} a bien le droit de supprimer des pétitions dans l'orga {orga}"
                          .format(user=pytitionuser, orga=org))
                    petition.delete()
                    return JsonResponse({})
                else:
                    print("L'utilisateur n'a pas les droits, dans cette orga, de supprimer une pétition")
    return JsonResponse({}, status=403)


@login_required
def petition_publish(request):
    petition_id = request.GET.get('id', '')
    pytitionuser = get_session_user(request)
    petition = petition_from_id(petition_id)

    if petition in pytitionuser.petitions.all():
        petition.publish()
        return JsonResponse({})
    else:
        for org in pytitionuser.organizations.all():
            if petition in org.petitions.all():
                userperms = pytitionuser.permissions.get(organization=org)
                if userperms.can_modify_petitions:
                    petition.publish()
                    return JsonResponse({})

    return JsonResponse({}, status=403)


@login_required
def petition_unpublish(request):
    petition_id = request.GET.get('id', '')
    pytitionuser = get_session_user(request)
    petition = petition_from_id(petition_id)

    if petition in pytitionuser.petitions.all():
        petition.unpublish()
        return JsonResponse({})
    else:
        for org in pytitionuser.organizations.all():
            if petition in org.petitions.all():
                userperms = pytitionuser.permissions.get(organization=org)
                if userperms.can_modify_petitions:
                    petition.unpublish()
                    return JsonResponse({})

    return JsonResponse({}, status=403)


@login_required
def edit_petition(request, petition_id):
    petition = petition_from_id(petition_id)

    org = None
    user = None
    if petition.organization_set.count() > 0:
        org = petition.organization_set.get()
    elif petition.pytitionuser_set.count() > 0:
        user = petition.pytitionuser_set.get()
    else:
        return HttpResponse(status=500)

    pytitionuser = get_session_user(request)

    if org:
        if pytitionuser not in org.members.all():
            return HttpResponseForbidden(_("You are not a member of this organization"))

        try:
            permissions = pytitionuser.permissions.get(organization=org)
        except:
            return HttpResponse(
                _("Internal error, cannot find your permissions attached to this organization (\'{orgname}\')"
                  .format(orgname=org.name)), status=500)

        if not permissions.can_modify_permissions:
            return HttpResponseForbidden(_("You don't have permission to edit petitions in this organization"))

    if user:
        if user != pytitionuser:
            return HttpResponseForbidden(_("You are not the owner of this petition"))


    if request.method == "POST":

        if 'content_form_submitted' in request.POST:
            content_form = ContentForm(request.POST)
            if content_form.is_valid():
                petition.title = content_form.cleaned_data['title']
                petition.text = content_form.cleaned_data['text']
                petition.side_text = content_form.cleaned_data['side_text']
                petition.footer_text = content_form.cleaned_data['footer_text']
                petition.footer_links = content_form.cleaned_data['footer_links']
                petition.sign_form_footer = content_form.cleaned_data['sign_form_footer']
                petition.save()
        else:
            content_form = ContentForm({f: getattr(petition, f) for f in ContentForm.base_fields})


        if 'email_form_submitted' in request.POST:
            email_form = EmailForm(request.POST)
            if email_form.is_valid():
                petition.use_custom_email_settings = email_form.cleaned_data['use_custom_email_settings']
                petition.confirmation_email_sender = email_form.cleaned_data['confirmation_email_sender']
                petition.confirmation_email_smtp_host = email_form.cleaned_data['confirmation_email_smtp_host']
                petition.confirmation_email_smtp_port = email_form.cleaned_data['confirmation_email_smtp_port']
                petition.confirmation_email_smtp_user = email_form.cleaned_data['confirmation_email_smtp_user']
                petition.confirmation_email_smtp_password = email_form.cleaned_data['confirmation_email_smtp_password']
                petition.confirmation_email_smtp_tls = email_form.cleaned_data['confirmation_email_smtp_tls']
                petition.confirmation_email_smtp_starttls = email_form.cleaned_data['confirmation_email_smtp_starttls']
                petition.save()
        else:
            email_form = EmailForm({f: getattr(petition, f) for f in EmailForm.base_fields})

        if 'social_network_form_submitted' in request.POST:
            social_network_form = SocialNetworkForm(request.POST)
            if social_network_form.is_valid():
                petition.twitter_description = social_network_form.cleaned_data['twitter_description']
                petition.twitter_image = social_network_form.cleaned_data['twitter_image']
                petition.org_twitter_handle = social_network_form.cleaned_data['org_twitter_handle']
                petition.save()
        else:
            social_network_form = SocialNetworkForm({f: getattr(petition, f) for f in SocialNetworkForm.base_fields})

        if 'newsletter_form_submitted' in request.POST:
            newsletter_form = NewsletterForm(request.POST)
            if newsletter_form.is_valid():
                petition.has_newsletter = newsletter_form.cleaned_data['has_newsletter']
                petition.newsletter_subscribe_http_data = newsletter_form.cleaned_data['newsletter_subscribe_http_data']
                petition.newsletter_subscribe_http_mailfield = newsletter_form.cleaned_data['newsletter_subscribe_http_mailfield']
                petition.newsletter_subscribe_http_url = newsletter_form.cleaned_data['newsletter_subscribe_http_url']
                petition.newsletter_subscribe_mail_subject = newsletter_form.cleaned_data['newsletter_subscribe_mail_subject']
                petition.newsletter_subscribe_mail_from = newsletter_form.cleaned_data['newsletter_subscribe_mail_from']
                petition.newsletter_subscribe_mail_to = newsletter_form.cleaned_data['newsletter_subscribe_mail_to']
                petition.newsletter_subscribe_method = newsletter_form.cleaned_data['newsletter_subscribe_method']
                petition.newsletter_subscribe_mail_smtp_host = newsletter_form.cleaned_data['newsletter_subscribe_mail_smtp_host']
                petition.newsletter_subscribe_mail_smtp_port = newsletter_form.cleaned_data['newsletter_subscribe_mail_smtp_port']
                petition.newsletter_subscribe_mail_smtp_user = newsletter_form.cleaned_data['newsletter_subscribe_mail_smtp_user']
                petition.newsletter_subscribe_mail_smtp_password = newsletter_form.cleaned_data['newsletter_subscribe_mail_smtp_password']
                petition.newsletter_subscribe_mail_smtp_tls = newsletter_form.cleaned_data['newsletter_subscribe_mail_smtp_tls']
                petition.newsletter_subscribe_mail_smtp_starttls = newsletter_form.cleaned_data['newsletter_subscribe_mail_smtp_starttls']
                petition.save()
        else:
            newsletter_form = NewsletterForm({f: getattr(petition, f) for f in NewsletterForm.base_fields})
    else:
        content_form = ContentForm({f: getattr(petition, f) for f in ContentForm.base_fields})
        email_form = EmailForm({f: getattr(petition, f) for f in EmailForm.base_fields})
        social_network_form = SocialNetworkForm({f: getattr(petition, f) for f in SocialNetworkForm.base_fields})
        newsletter_form = NewsletterForm({f: getattr(petition, f) for f in NewsletterForm.base_fields})

    ctx = {'user': pytitionuser,
           'content_form': content_form,
           'email_form': email_form,
           'social_network_form': social_network_form,
           'newsletter_form': newsletter_form,
           'petition': petition}

    if org:
        ctx.update({'org': org,
                    'user_permissions': permissions,
                    'base_template': 'petition/org_base.html'})

    if user:
        ctx.update({'base_template': 'petition/user_base.html'})

    return render(request, "petition/edit_petition.html", ctx)