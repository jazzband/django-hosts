from django import forms

class RedirectForm(forms.Form):
    domain = forms.CharField()
    path = forms.CharField()
