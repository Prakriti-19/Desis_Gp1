from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User



class UserRegisterForm(UserCreationForm):
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Username"}
        ),
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "name@example.com"}
        ),
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Password"}
        ),
    )
    password2 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Retype password"}
        ),
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class UserLoginForm(forms.Form):
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Username"}
        ),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Password"}
        ),
    )
