from django.conf.urls import url

from . import views
from petition.views import PetitionList, PetitionDetail

urlpatterns = [
    # ex: /polls/
    url(r'^$', views.index, name='index'),
    # ex: /polls/5/
    url(r'^(?P<petition_id>[0-9]+)/$', views.detail, name='detail'),
    # ex: /polls/5/vote/
    url(r'^(?P<petition_id>[0-9]+)/get_json_data$', views.get_json_data, name='get_json_data'),
    url(r'^confirm/(?P<hash>.*)$', views.confirm, name='confirm'),
    url(r'^show/(?P<pk>[0-9]+)/$', PetitionDetail.as_view())
]