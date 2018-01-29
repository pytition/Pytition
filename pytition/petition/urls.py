from django.conf.urls import url

from . import views

urlpatterns = [
    # ex: /polls/
    url(r'^$', views.index, name='index'),
    # ex: /polls/5/
    url(r'^(?P<petition_id>[0-9]+)/$', views.detail, name='detail'),
    # ex: /polls/5/vote/
    url(r'^(?P<petition_id>[0-9]+)/get_json_data$', views.get_json_data, name='get_json_data'),
    url(r'^confirm/(?P<petition_id>[0-9]+)/(?P<hash>.*)$', views.detail, {'confirm': True}, name='confirm'),
    url(r'^(?P<petition_id>[0-9]+)/get_csv_signature$', views.get_csv_signature, name='get_csv_signature'),
]