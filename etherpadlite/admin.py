# -*- coding: utf-8 -*- 

from etherpadlite.models import *
from django.contrib import admin

class PadAuthorAdmin(admin.ModelAdmin):
   list_display = ('__unicode__',)

class PadAdmin(admin.ModelAdmin):
   list_display = ('__unicode__',)

admin.site.register(PadServer)
admin.site.register(PadGroup)
admin.site.register(PadAuthor, PadAuthorAdmin)
admin.site.register(Pad, PadAdmin)
