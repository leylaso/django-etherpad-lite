# -*- coding: utf-8 -*-

# Python imports
import datetime
import time
import urllib
from urlparse import urlparse

# Framework imports
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.template import RequestContext

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now

from django.shortcuts import render_to_response, get_object_or_404


# additional imports
from py_etherpad import EtherpadLiteClient

# local imports
from etherpadlite.models import *
from etherpadlite import forms
from etherpadlite import config


@login_required
def padCreate(request, pk):
    """ Create a named pad for the given group
    """
    group = get_object_or_404(PadGroup, pk=pk)

    if request.method == 'POST':  # Process the form
        form = forms.PadCreate(request.POST)
        if form.is_valid():
            pad = Pad(
                name=form.cleaned_data['name'],
                server=group.server,
                group=group
            )
            pad.save()
            return HttpResponseRedirect(reverse('etherpadlite_profile'))
    else:  # No form to process so create a fresh one
        form = forms.PadCreate({'group': group.groupID})

    con = {
        'form': form,
        'pk': pk,
        'title': _('Create pad in %(grp)s') % {'grp': group.__unicode__()}
    }
    con.update(csrf(request))
    return render_to_response(
        'etherpad-lite/padCreate.html',
        con,
        context_instance=RequestContext(request)
    )


@login_required
def padDelete(request, pk):
    """ Delete a given pad
    """
    pad = get_object_or_404(Pad, pk=pk)
    pad_group = pad.group
    if not pad_group.is_moderator(request.user):
        raise PermissionDenied
    # Any form submissions will send us back to the profile
    if request.method == 'POST':
        if 'confirm' in request.POST:
            pad.delete()
        return HttpResponseRedirect(reverse('etherpadlite_profile'))

    con = {
        'action': reverse('etherpadlite_delete_pad', kwargs={'pk': pk}),
        'question': _('Really delete this pad?'),
        'title': _('Deleting %(pad)s') % {'pad': pad.__unicode__()}
    }
    con.update(csrf(request))
    return render_to_response(
        'etherpad-lite/confirm.html',
        con,
        context_instance=RequestContext(request)
    )


@login_required
def groupCreate(request):
    """ Create a new Group, a PadGroup and add this group to the creator of the
    group.
    """
    message = ""
    if request.method == 'POST':  # Process the form
        form = forms.GroupCreate(request.POST)
        if form.is_valid():
            group = form.save()
            # temporarily it is not nessessary to specify a server, so we take
            # the first one we get.
            server = PadServer.objects.all()[0]
            pad_group = PadGroup(group=group, server=server)
            pad_group.save()
            pad_group.moderators.add(request.user)
            request.user.groups.add(group)
            return HttpResponseRedirect(reverse('etherpadlite_profile'))
        else:
            message = _("This Groupname is allready in use or invalid.")
    else:  # No form to process so create a fresh one
        form = forms.GroupCreate()
    con = {
        'form': form,
        'title': _('Create a new Group'),
        'message': message,
    }
    con.update(csrf(request))
    return render_to_response(
        'etherpad-lite/groupCreate.html',
        con,
        context_instance=RequestContext(request)
    )


@login_required
def groupDelete(request, pk):
    """ Delete a given group. This is only possible, if the group hat also a
    PadGroup
    """
    group = get_object_or_404(Group, pk=pk)
    pad_group = get_object_or_404(PadGroup, group=group)
    if not pad_group.is_moderator(request.user):
        raise PermissionDenied
    # Any form submissions will send us back to the profile
    if request.method == 'POST':
        if 'confirm' in request.POST:
            group.delete()
        return HttpResponseRedirect(reverse('etherpadlite_profile'))

    con = {
        'action': reverse('etherpadlite_delete_group', kwargs={'pk': pk}),
        'question': _('Really delete this group?'),
        'title': _('Deleting %(group)s') % {'group': group.__unicode__()}
    }
    con.update(csrf(request))
    return render_to_response(
        'etherpad-lite/confirm.html',
        con,
        context_instance=RequestContext(request)
    )


@login_required
def groupManage(request, pk):
    """ Manage a given Group. In this View the user is able to add and remove
    People from a group
    """
    group = get_object_or_404(Group, pk=pk)
    pad_group = get_object_or_404(PadGroup, group=group)
    if not pad_group.is_moderator(request.user):
        raise PermissionDenied
    # Any form submissions will send us back to the profile
    con = {
        'users': group.user_set.all(),
        'group': group,
        'moderators': pad_group.moderators.all(),
        'messages': []
    }
    if request.method == 'POST':
        if 'userToRemove' in request.POST and 'userToRemove' in request.POST:
            for username in request.POST.getlist('userToRemove'):
                user = User.objects.filter(username=username)[0]
                user.groups.remove(group)
                con['messages'].append({
                    'text': _("Removed the following users from group: %s"
                        % (", ".join(request.POST.getlist('userToRemove')))),
                    'type': 'success'
                    }
                )
        if 'userToAdd' in request.POST and request.POST.get('userToAdd'):
            username = request.POST.get('userToAdd')
            user = User.objects.filter(username=username)
            if user:
                user = user[0]
                user.groups.add(group)
                con['messages'].append({
                    'text': _("Added user %s to group." % (user.username)),
                    'type': 'success'
                })
            else:
                con['messages'].append({
                    'text': _("No user with username %s." % (username)),
                    'type': 'error'
                })
        if 'isModerator' in request.POST:
            new_moderator_list = [User.objects.get(username=user)
                for user in request.POST.getlist('isModerator')]
            pad_group.moderators = new_moderator_list
        else:
            pad_group.moderators.add(request.user)
            con['messages'].append({
                'text': _("At least one moderator musst be added. Added " +
                    "active User."),
                'type': 'error'
            })
        con['moderators'] = pad_group.moderators.all()
    con.update(csrf(request))
    pad_group.save()
    # We have to check again. Its possible that the user removed himself.
    if not pad_group.is_moderator(request.user):
        raise PermissionDenied
    return render_to_response(
        'etherpad-lite/groupManage.html',
        con,
        context_instance=RequestContext(request)
    )


@login_required
def profile(request):
    """ Display a user profile containing etherpad groups and associated pads
    """
    name = request.user.__unicode__()

    try:  # Retrieve the corresponding padauthor object
        author = PadAuthor.objects.get(user=request.user)
    except PadAuthor.DoesNotExist:  # None exists, so create one
        author = PadAuthor(
            user=request.user,
            server=PadServer.objects.get(id=1)
        )
        author.save()
    author.GroupSynch()

    groups = {}
    for g in author.group.all():
        groups[g.__unicode__()] = {
            'group': g,
            'pads': Pad.objects.filter(group=g),
            'moderators': g.moderators.all()
        }
    return render_to_response(
        'etherpad-lite/profile.html',
        {
            'name': name,
            'author': author,
            'groups': groups
        },
        context_instance=RequestContext(request)
    )


@login_required
def pad(request, pk):
    """ Create and session and display an embedded pad
    """

    # Initialize some needed values
    pad = get_object_or_404(Pad, pk=pk)
    pad.modification_date = now()
    pad.save()
    padLink = pad.server.url + 'p/' + pad.group.groupID + '$' + \
        urllib.quote_plus(pad.name)
    server = urlparse(pad.server.url)
    author = PadAuthor.objects.get(user=request.user)

    if author not in pad.group.authors.all():
        response = render_to_response(
            'etherpad-lite/pad.html',
            {
                'pad': pad,
                'link': padLink,
                'server': server,
                'uname': author.user.__unicode__(),
                'error': _('You are not allowed to view or edit this pad')
            },
            context_instance=RequestContext(request)
        )
        return response

    # Create the session on the etherpad-lite side
    expires = datetime.datetime.utcnow() + datetime.timedelta(
        seconds=config.SESSION_LENGTH
    )
    epclient = EtherpadLiteClient(pad.server.apikey, pad.server.apiurl)

    try:
        result = epclient.createSession(
            pad.group.groupID,
            author.authorID,
            time.mktime(expires.timetuple()).__str__()
        )
    except Exception, e:
        response = render_to_response(
            'etherpad-lite/pad.html',
            {
                'pad': pad,
                'link': padLink,
                'server': server,
                'uname': author.user.__unicode__(),
                'error': _('etherpad-lite session request returned:') +
                ' "' + e.reason + '"'
            },
            context_instance=RequestContext(request)
        )
        return response

    # Set up the response
    response = render_to_response(
        'etherpad-lite/pad.html',
        {
            'pad': pad,
            'link': padLink,
            'server': server,
            'uname': author.user.__unicode__(),
            'error': False
        },
        context_instance=RequestContext(request)
    )

    # Delete the existing session first
    if ('sessionID' in request.COOKIES):
        try:
            epclient.deleteSession(request.COOKIES['sessionID'])
        except ValueError:
            # Sometimes the deleteSession function creates a sessionID does not
            # exist Exception during deletion process.
            pass
        response.delete_cookie('sessionID', server.hostname)
        response.delete_cookie('padSessionID')

    # Set the new session cookie for both the server and the local site
    response.set_cookie(
        'sessionID',
        value=result['sessionID'],
        expires=expires,
        domain=server.hostname,
        httponly=False
    )
    response.set_cookie(
        'padSessionID',
        value=result['sessionID'],
        expires=expires,
        httponly=False
    )
    return response
