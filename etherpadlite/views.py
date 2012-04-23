# -*- coding: utf-8 -*- 

from django.shortcuts import render_to_response, get_object_or_404
from etherpadlite.models import *
from etherpadlite import forms
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.context_processors import csrf
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _
from py_etherpad import EtherpadLiteClient

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

  con = {'form': form, 'pk': pk, 'title': _('Create pad in %(grp)s') % {'grp':group.__unicode__()}}
  con.update(csrf(request))
  return render_to_response('etherpad-lite/padCreate.html', 
                            con, 
                            context_instance=RequestContext(request))


@login_required(login_url='/etherpad')
def padDelete(request, pk):
  """Delete a given pad
  """
  pad = get_object_or_404(Pad, pk=pk)

  if request.method == 'POST': #Any form submissions will send us back to the profile
    if 'confirm' in request.POST: 
      pad.delete()
    return HttpResponseRedirect('/accounts/profile/')

  con = {'action': '/etherpad/delete/' + pk + '/', 'question':_('Really delete this pad?'), 'title': _('Deleting %(pad)s') % {'pad':pad.__unicode__()}}
  con.update(csrf(request))
  return render_to_response('etherpad-lite/confirm.html', 
                            con, 
                            context_instance=RequestContext(request))


@login_required(login_url='/etherpad')
def profile(request):
  """Display a user profile containing etherpad groups and associated pads
  """
  name = request.user.__unicode__()

  try: # Retrieve the corresponding padauthor object
    author = PadAuthor.objects.get(user=request.user)
  except PadAuthor.DoesNotExist: # None exists, so create one
    author = PadAuthor(user=request.user, server=PadServer.objects.get(id=1))
    author.save()
  author.GroupSynch()

  groups = {}
  for g in author.group.all():
    groups[g.__unicode__()] = {'group': g, 'pads': Pad.objects.filter(group=g)}

  return render_to_response('etherpad-lite/profile.html', 
                            {'name': name, 'author': author, 'groups':groups},
                            context_instance=RequestContext(request))


@login_required(login_url='/etherpad')
def pad(request, pk):
  """Create and session and display an embedded pad
  """
  import datetime
  import time
  from etherpadlite import config
  from urlparse import urlparse
  from django.conf import settings

  # Initialize some needed values
  pad = get_object_or_404(Pad, pk=pk)

  import urllib

  padLink = pad.server.url + 'p/' + pad.group.groupID + '$' + urllib.quote_plus(pad.name)
  server = urlparse(pad.server.url)
  author = PadAuthor.objects.get(user=request.user)

  # Create the session on the etherpad-lite side
  expires = datetime.datetime.utcnow() + datetime.timedelta(seconds=config.SESSION_LENGTH)

  epclient = EtherpadLiteClient(pad.server.apikey, pad.server.apiurl)

  default_author_name_mapper = lambda user: user.__unicode__()
  author_name_mapper = getattr(settings, 'ETHERPAD_AUTHOR_NAME_MAPPER', default_author_name_mapper)

  default_etherpad_settings = {
      "showControls": True,
      "showChat": True,
      "alwaysShowChat": False,
      "showLineNumbers": False,
      "useMonospaceFont": False,
      "noColors": False,
      "hideQRCode": True,
      "rtl": False,
      "userName": author_name_mapper(author.user),
  }

  pad_settings = default_etherpad_settings
  pad_settings.update(getattr(settings, 'ETHERPAD_SETTINGS', {}))

  for key, value in pad_settings.items():
    if value == True:
      pad_settings[key] = 'true'
    elif value == False:
      pad_settings[key] = 'false'

  import urllib

  try:
    result = epclient.createSession(pad.group.groupID, author.authorID, time.mktime(expires.timetuple()).__str__())
  except Exception, e:
    response = render_to_response('etherpad-lite/pad.html',
                                   {'pad': pad, 
                                    'link': padLink, 
                                    'server':server, 
                                    'querystring': urllib.urlencode(pad_settings).replace('+', ' '),
                                    'error':_('etherpad-lite session request returned:') + ' "' + e.reason + '"'},
                                 context_instance=RequestContext(request))
    return response
    

  # Set up the response
  response = render_to_response('etherpad-lite/pad.html',
                                {'pad': pad, 
                                 'link': padLink, 
                                 'server':server, 
                                 'querystring': urllib.urlencode(pad_settings).replace('+', ' '),
                                 'error':False},
                                context_instance=RequestContext(request))


  if ('padSessionID' in request.COOKIES): # Delete the existing session first
    result2 = epclient.deleteSession(request.COOKIES['sessionID'])
    response.delete_cookie('sessionID', server.hostname)
    response.delete_cookie('padSessionID')

  # Set the new session cookie for both the server and the local site
  response.set_cookie('sessionID',
                      value=result['sessionID'],
                      expires=expires,
                      domain=server.hostname,
                      httponly=False)
  response.set_cookie('padSessionID',
                      value=result['sessionID'],
                      expires=expires,
                      httponly=False)

  return response
