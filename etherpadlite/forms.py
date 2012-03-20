from django import forms
from django.utils.translation import ugettext as _

class PadCreate(forms.Form):
  name = forms.CharField(label=_("Name"))
  group = forms.CharField(widget=forms.HiddenInput)
