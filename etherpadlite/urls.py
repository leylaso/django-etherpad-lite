from django.conf.urls.defaults import patterns, url

from etherpadlite.models import *


urlpatterns = patterns(
    '',
    url(r'^etherpad$', 'django.contrib.auth.views.login',
        {'template_name': 'etherpad-lite/login.html'},
        name='etherpadlite_login'),
    url(r'^logout$', 'django.contrib.auth.views.logout',
        {'template_name': 'etherpad-lite/logout.html'},
        name="etherpadlite_logout"),
    url(r'^accounts/profile/$', 'etherpadlite.views.profile',
        name="etherpadlite_profile"),

    url(r'^etherpad/view/(?P<group_slug>[-\w]+)/(?P<pad_slug>[-\w]+)/$', 'etherpadlite.views.pad',
        name="etherpadlite_view_pad"),
    url(r'^etherpad/create/(?P<slug>[-\w]+)/$', 'etherpadlite.views.padCreate',
        name="etherpadlite_create_pad"),
    url(r'^etherpad/delete/(?P<group_slug>[-\w]+)/(?P<pad_slug>[-\w]+)/$', 'etherpadlite.views.padDelete',
        name="etherpadlite_delete_pad"),

    url(r'^group/create/$', 'etherpadlite.views.groupCreate',
        name="etherpadlite_create_group"),
    url(r'^group/delete/(?P<slug>[-\w]+)/$', 'etherpadlite.views.groupDelete',
        name="etherpadlite_delete_group"),
    url(r'^group/manage/(?P<slug>[-\w]+)/$', 'etherpadlite.views.groupManage',
        name="etherpadlite_manage_group"),
)
