from django.conf.urls import url

from . import views

urlpatterns = [
    # ex: /polls/
    url(r'^$', views.index, name='index'),
    # ex: /polls/5/
    url(r'^(?P<petition_id>[0-9]+)/$', views.detail, name='detail'),
    # ex: /polls/5/vote/
    url(r'^(?P<petition_id>[0-9]+)/confirm/(?P<confirmation_hash>.*)$', views.confirm, name='confirm'),
    url(r'^(?P<petition_id>[0-9]+)/get_csv_signature$', views.get_csv_signature, {'only_confirmed': False},
        name='get_csv_signature'),
    url(r'^(?P<petition_id>[0-9]+)/get_csv_confirmed_signature$', views.get_csv_signature, {'only_confirmed': True},
        name='get_csv_confirmed_signature'),
    url(r'^resend/(?P<signature_id>[0-9]+)', views.go_send_confirmation_email, name='resend_confirmation_email'),
    url(r'^(?P<petition_id>[0-9]+)/sign', views.create_signature, name='create_signature'),
    url(r'^org/(?P<org_name>[^/]*)$', views.org_dashboard, name='org_dashboard'),
    url(r'^org/(?P<org_name>[^/]*)/leave$', views.leave_org, name="leave_org"),
    url(r'^org/(?P<org_name>[^/]*)/add_user$', views.org_add_user, name='org_add_user'),
    url(r'^user/(?P<user_name>[^/]*)$', views.user_profile, name='user_profile'),
    url(r'^user/(?P<user_name>[^/]*)/dashboard$', views.user_dashboard, name='user_dashboard'),
    url(r'^get_user_list', views.get_user_list, name='get_user_list'),
]