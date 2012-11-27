from django import forms
from django.contrib.auth.models import Group
from django.utils.translation import ugettext_lazy as _


class PadCreate(forms.Form):
    name = forms.CharField(label=_("Name"))
    group = forms.CharField(widget=forms.HiddenInput)


class GroupCreate(forms.ModelForm):
    class Meta:
        model = Group
        exclude = ('permissions')
