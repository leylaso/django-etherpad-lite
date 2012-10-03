from django.conf.urls.defaults import patterns, url

from etherpadlite.models import *


urlpatterns = patterns(
    '',
    url(r'^$', 'django.contrib.auth.views.login',
        {'template_name': 'etherpad-lite/login.html'}),
    url(r'^etherpad$', 'django.contrib.auth.views.login',
        {'template_name': 'etherpad-lite/login.html'}),
    url(r'^logout$', 'django.contrib.auth.views.logout',
        {'template_name': 'etherpad-lite/logout.html'}),
    url(r'^accounts/profile/$', 'etherpadlite.views.profile'),
    url(r'^etherpad/(?P<pk>\d+)/$', 'etherpadlite.views.pad'),
    url(r'^etherpad/create/(?P<pk>\d+)/$', 'etherpadlite.views.padCreate'),
    url(r'^etherpad/delete/(?P<pk>\d+)/$', 'etherpadlite.views.padDelete'),
    url(r'^group/create/$', 'etherpadlite.views.groupCreate')
)
