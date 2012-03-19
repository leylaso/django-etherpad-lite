from django.conf.urls.defaults import patterns, include, url
from django_etherpad_lite.models import *
from django.views.generic import DetailView, ListView

urlpatterns = patterns('',

  url(r'^$', 'django.contrib.auth.views.login', {'template_name': 'etherpad-lite/login.html'}),
  url(r'^etherpad$', 'django.contrib.auth.views.login', {'template_name': 'etherpad-lite/login.html'}),
  url(r'^logout$', 'django.contrib.auth.views.logout', {'template_name': 'etherpad-lite/logout.html'}),
  url(r'^accounts/profile/$', 'django_etherpad_lite.views.profile'),
  url(r'^etherpad/(?P<pk>\d+)/$', 'django_etherpad_lite.views.pad'),
  url(r'^etherpad/create/(?P<pk>\d+)/$', 'django_etherpad_lite.views.padCreate'),
  url(r'^etherpad/delete/(?P<pk>\d+)/$', 'django_etherpad_lite.views.padDelete')
)
