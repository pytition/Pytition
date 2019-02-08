from django.conf.urls import url, include

from . import views
from .forms import PytitionUserCreationForm
from .views import PetitionCreationWizard
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<petition_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^(?P<petition_id>[0-9]+)/confirm/(?P<confirmation_hash>.*)$', views.confirm, name='confirm'),
    url(r'^(?P<petition_id>[0-9]+)/get_csv_signature$', views.get_csv_signature, {'only_confirmed': False},
        name='get_csv_signature'),
    url(r'^(?P<petition_id>[0-9]+)/get_csv_confirmed_signature$', views.get_csv_signature, {'only_confirmed': True},
        name='get_csv_confirmed_signature'),
    url(r'^resend/(?P<signature_id>[0-9]+)', views.go_send_confirmation_email, name='resend_confirmation_email'),
    url(r'^(?P<petition_id>[0-9]+)/sign', views.create_signature, name='create_signature'),
    url(r'^(?P<petition_id>[0-9]+)/show_signatures', views.show_signatures, name='show_signatures'),
    url(r'^petition_delete', views.petition_delete, name='petition_delete'),
    url(r'^petition_publish', views.petition_publish, name='petition_publish'),
    url(r'^petition_unpublish', views.petition_unpublish, name='petition_unpublish'),
    url(r'^org/(?P<org_name>[^/]+)$', views.org_profile, name='org_profile'),
    url(r'^org/(?P<org_name>[^/]+)/dashboard$', views.org_dashboard, name='org_dashboard'),
    url(r'^leave_org$', views.leave_org, name="leave_org"),
    url(r'^org/(?P<org_name>[^/]+)/add_user$', views.org_add_user, name='org_add_user'),
    url(r'^org/(?P<org_name>[^/]+)/new_template$', views.new_template, name='org_new_template'),
    url(r'^edit_template/(?P<template_id>[^/]+)$', views.edit_template, name='edit_template'),
    url(r'^ptemplate_fav_toggle$', views.ptemplate_fav_toggle, name='ptemplate_fav_toggle'),
    url(r'^org/(?P<org_name>[^/]+)/delete_member$', views.org_delete_member, name='org_delete_member'),
    url(r'^org/(?P<org_name>[^/]+)/edit_user_permissions/(?P<user_name>[^/]+)$', views.org_edit_user_perms,
        name='org_edit_user_perms'),
    url(r'^org/(?P<org_name>[^/]+)/set_user_permissions/(?P<user_name>[^/]+)$', views.org_set_user_perms,
        name='org_set_user_perms'),
    url(r'^edit_petition/(?P<petition_id>[0-9]+)$', views.edit_petition,
        name='edit_petition'),
    url(r'^user/dashboard$', views.user_dashboard, name='user_dashboard'),
    url(r'^user/new_template$', views.new_template, name='user_new_template'),
    url(r'^user/(?P<user_name>[^/]+)$', views.user_profile, name='user_profile'),
    url(r'^user/(?P<user_name>[^/]+)/create_petition$', views.user_create_petition, name='user_create_petition'),
    url(r'^template_delete$', views.template_delete, name='template_delete'),
    url(r'^get_user_list', views.get_user_list, name='get_user_list'),
    url(r'^invite_accept/$', views.invite_accept, name='invite_accept'),
    url(r'^invite_dismiss/$', views.invite_dismiss, name='invite_dismiss'),
    url(r'^wizard/org/(?P<org_name>[^/]+)/new_petition$', PetitionCreationWizard.as_view(views.WizardForms),
        name='org_petition_wizard'),
    url(r'^wizard/user/new_petition$', PetitionCreationWizard.as_view(views.WizardForms),
        name='user_petition_wizard'),
    url('^', include('django.contrib.auth.urls')),
    url('^register/',
        CreateView.as_view(template_name='registration/register.html', form_class=PytitionUserCreationForm,
                           success_url=reverse_lazy("login")), name="register"),
]