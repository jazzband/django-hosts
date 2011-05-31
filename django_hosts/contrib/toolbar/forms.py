from django import forms

class RedirectForm(forms.Form):
    host = forms.CharField()
    path = forms.CharField()
