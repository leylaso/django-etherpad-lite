from django import forms

class PadCreate(forms.Form):
  name = forms.CharField()
  group = forms.CharField(widget=forms.HiddenInput)
