# -*- coding: utf-8 -*- 

from django_etherpad_lite.models import *
from django.contrib import admin

class PadAuthorAdmin(admin.ModelAdmin):
   list_display = ('__unicode__',)
   actions = ['EtherMap']
   def EtherMap(modeladmin, request, queryset):
     for a in queryset.all():
       a.EtherMap()
   EtherMap.short_description = "Map selected authors to their etherpad servers"


admin.site.register(PadServer)
admin.site.register(PadGroup)
admin.site.register(PadAuthor, PadAuthorAdmin)
admin.site.register(Pad)
