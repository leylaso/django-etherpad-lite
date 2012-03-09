# -*- coding: utf-8 -*- 

from django_etherpad_lite.models import *
from django.contrib import admin

class PadServerAdmin(admin.ModelAdmin):
   list_display = ('__unicode__',)  

admin.site.register(PadServer, PadServerAdmin)
admin.site.register(PadGroup)
admin.site.register(PadAuthor)
admin.site.register(Pad)
