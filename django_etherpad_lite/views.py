# -*- coding: utf-8 -*- 

from django.shortcuts import render_to_response, get_object_or_404
from django_etherpad_lite.models import *
from django_etherpad_lite import forms
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.core.context_processors import csrf
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _

@login_required(login_url='/etherpad')
def padCreate(request, pk):
  """Create a named pad for the given group
  """
  group = get_object_or_404(PadGroup, pk=pk)

  if request.method == 'POST': # Process the form
    form = forms.PadCreate(request.POST)
    if form.is_valid():
      pad = Pad(name=form.cleaned_data['name'], server=group.server, group=group)
      pad.save()
      return HttpResponseRedirect('/accounts/profile/')
  else: # No form to process so create a fresh one
    form = forms.PadCreate({'group':group.groupID})

  con = {'form': form, 'pk': pk}
  con.update(csrf(request))
  return render_to_response('etherpad-lite/padCreate.html', con)


@login_required(login_url='/etherpad')
def padDelete(request, pk):
  """Delete a given pad
  """
  pad = get_object_or_404(Pad, pk=pk)

  if request.method == 'POST': #Any form submissions will send us back to the profile
    if 'confirm' in request.POST: 
      pad.delete()
    return HttpResponseRedirect('/accounts/profile/')

  con = {'action': '/etherpad/delete/' + pk + '/', 'question':_('Really delete this pad?')}
  con.update(csrf(request))
  return render_to_response('etherpad-lite/confirm.html', con)


@login_required(login_url='/etherpad')
def profile(request):
  """Display a user profile containing etherpad groups and associated pads
  """
  name = request.user.__unicode__()
  
  try: # Retrieve the corresponding padauthor object
    author = PadAuthor.objects.get(user=request.user)
  except PadAuthor.DoesNotExist: # None exists, so create one
    author = PadAuthor(user=request.user, server=PadServer.objects.get(id=1))
  author.save() # Always resave, to synchronize groups and get mappings from the etherpad server

  groups = {}
  for g in author.group.all():
    groups[g.__unicode__()] = {'group': g, 'pads': Pad.objects.filter(group=g)}

  return render_to_response('etherpad-lite/profile.html', {'name': name, 'author': author, 'groups':groups});


@login_required(login_url='/etherpad')
def pad(request, pk):
  """Create and session and display an embedded pad
  """
  import datetime
  import time
  from django_etherpad_lite import simplecurl
  from django_etherpad_lite import config
  from urlparse import urlparse

  # Initialize some needed values
  pad = get_object_or_404(Pad, pk=pk)
  padLink = pad.server.url + 'p/' + pad.group.groupID + '$' + pad.name
  server = urlparse(pad.server.url)
  author = PadAuthor.objects.get(user=request.user)

  # Determine an expiry date for the session
  expires = datetime.datetime.utcnow() + datetime.timedelta(seconds=config.SESSION_LENGTH)
  expireStr = datetime.datetime.strftime(expires, "%a, %d-%b-%Y %H:%M:%S GMT")

  # Create the session on the etherpad-lite side
  sessReq = pad.server.url + 'api/1/createSession?apikey=' + pad.server.apikey + '&groupID=' + pad.group.groupID + '&authorID=' + author.authorID + '&validUntil=' + time.mktime(expires.timetuple()).__str__()
  sessResp = simplecurl.json(sessReq)

  # Craft a response and add the necessary values from etherpad-lite to the cookie
  response = render_to_response('etherpad-lite/pad.html', {'pad': pad, 'link': padLink, 'server':server, 'uname': author.user.__unicode__()});
  response.set_cookie('sessionID', sessResp['data']['sessionID'], max_age=config.SESSION_LENGTH, expires=expireStr, domain=server.hostname)

  return response
