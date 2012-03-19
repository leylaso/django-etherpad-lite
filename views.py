# -*- coding: utf-8 -*- 

from django.shortcuts import render_to_response, get_object_or_404
from django_etherpad_lite.models import *
from django_etherpad_lite import forms
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.admin.views.decorators import staff_member_required
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.context_processors import csrf
import datetime
import time
from django_etherpad_lite import simplecurl
from urlparse import urlparse

DJANGO_ETHERPAD_LITE_SESSION_LENGTH = 45 * 24 * 60 * 60

def padCreate(request, pk):
  group = get_object_or_404(PadGroup, pk=pk)
  if request.method == 'POST':
    form = forms.PadCreate(request.POST)
    if form.is_valid():
      pad = Pad(name=form.cleaned_data['name'], server=group.server, group=group)
      pad.save()
      pad.Create()
      return HttpResponseRedirect('/accounts/profile/')
  else:
    form = forms.PadCreate({'group':group.groupID})
  con = {'form': form, 'pk': pk}
  con.update(csrf(request))
  return render_to_response('etherpad-lite/padCreate.html', con)

def profile(request):
  name = request.user.__unicode__()
  
  # Retrieve the corresponding padauthor object - if none exists, create one
  try:
    author = PadAuthor.objects.get(user=request.user)
  except PadAuthor.DoesNotExist:
    author = PadAuthor(user=request.user, server=PadServer.objects.get(id=1))
    author.save()
    author.GroupSynch()
    author.EtherMap()

  groups = {}
  for g in author.group.all():
    groups[g.__unicode__()] = {'group': g, 'pads': Pad.objects.filter(group=g)}
  return render_to_response('etherpad-lite/profile.html', {'name': name, 'author': author, 'groups':groups});

def pad(request, pk):
  pad = get_object_or_404(Pad, pk=pk)
  padLink = pad.server.url + 'p/' + pad.group.groupID + '$' + pad.name
  server = urlparse(pad.server.url)

  author = PadAuthor.objects.get(user=request.user)
  expires = datetime.datetime.utcnow() + datetime.timedelta(seconds=DJANGO_ETHERPAD_LITE_SESSION_LENGTH)
  expireStr = datetime.datetime.strftime(expires, "%a, %d-%b-%Y %H:%M:%S GMT")
  sessReq = pad.server.url + 'api/1/createSession?apikey=' + pad.server.apikey + '&groupID=' + pad.group.groupID + '&authorID=' + author.authorID + '&validUntil=' + time.mktime(expires.timetuple()).__str__()
  sessResp = simplecurl.json(sessReq)

  response = render_to_response('etherpad-lite/pad.html', {'pad': pad, 'link': padLink, 'server':server, 'uname': author.user.__unicode__()});
  response.set_cookie('sessionID', sessResp['data']['sessionID'], max_age=DJANGO_ETHERPAD_LITE_SESSION_LENGTH, expires=expireStr, domain=server.hostname)

  return response
