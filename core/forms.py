from django import forms

class LoginForm(forms.Form):
    user = forms.CharField(required=True)
    password = forms.CharField(required=True,widget=forms.PasswordInput)