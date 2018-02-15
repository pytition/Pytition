from django.conf.urls import url

from . import views

urlpatterns = [
    # ex: /polls/
    url(r'^$', views.index, name='index'),
    # ex: /polls/5/
    url(r'^(?P<petition_id>[0-9]+)/$', views.detail, name='detail'),
    # ex: /polls/5/vote/
    url(r'^(?P<petition_id>[0-9]+)/get_json_data$', views.get_json_data, name='get_json_data'),
    url(r'^confirm/(?P<petition_id>[0-9]+)/(?P<confirmation_hash>.*)$', views.detail, {'do_confirmation': True},
        name='confirm'),
    url(r'^(?P<petition_id>[0-9]+)/get_csv_signature$', views.get_csv_signature, {'only_confirmed': False},
        name='get_csv_signature'),
    url(r'^(?P<petition_id>[0-9]+)/get_csv_confirmed_signature$', views.get_csv_signature, {'only_confirmed': True},
        name='get_csv_confirmed_signature'),
    url(r'^resend/(?P<signature_id>[0-9]+)', views.go_send_confirmation_email, name='resend_confirmation_email'),
]