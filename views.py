# -*- coding: utf-8 -*- 

from django.shortcuts import render_to_response, get_object_or_404
from django_etherpad_lite.models import *
from django.db.models import Count
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import datetime

def profile(request):
  name = request.user.__unicode__()
  author = PadAuthor.objects.get(user=request.user)
  groups = {}
  for g in author.group.all():
    groups[g.__unicode__()] = Pad.objects.filter(group=g)
  return render_to_response('etherpad-lite/profile.html', {'name': name, 'author': author, 'groups':groups});
