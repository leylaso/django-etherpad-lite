from django.conf.urls.defaults import patterns, include, url
from django_etherpad_lite.models import *
from django.views.generic import DetailView, ListView

urlpatterns = patterns('',

  url(r'^$', 'django.contrib.auth.views.login', {'template_name': 'etherpad-lite/login.html'}),
  url(r'^etherpad$', 'django.contrib.auth.views.login', {'template_name': 'etherpad-lite/login.html'}),
  url(r'^logout$', 'django.contrib.auth.views.logout', {'template_name': 'etherpad-lite/logout.html'}),
  url(r'^accounts/profile/$', 'django_etherpad_lite.views.profile')
)
