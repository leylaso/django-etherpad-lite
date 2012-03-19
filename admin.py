# -*- coding: utf-8 -*- 

from django_etherpad_lite.models import *
from django.contrib import admin

class PadAuthorAdmin(admin.ModelAdmin):
   list_display = ('__unicode__',)

class PadAdmin(admin.ModelAdmin):
   list_display = ('__unicode__',)
   actions = ['Create']
   def Create(modeladmin, request, queryset):
     for a in queryset.all():
       a.Create()
   Create.short_description = "Create these pads on their respective servers"

admin.site.register(PadServer)
admin.site.register(PadGroup)
admin.site.register(PadAuthor, PadAuthorAdmin)
admin.site.register(Pad, PadAdmin)
