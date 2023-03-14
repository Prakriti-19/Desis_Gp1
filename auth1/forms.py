from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from inventory.models import ngo,donor,pincode
from django.forms import ModelForm, PasswordInput, Select, TextInput, EmailInput

'''
The class ngoUserCreationForm is a subclass of the UserCreationForm provided by Django.
The Meta class is used to provide additional metadata for the ngo model and is an example of abstraction. 
'''
class ngoUserCreationForm(UserCreationForm):
    pincode = forms.ModelChoiceField(queryset=pincode.objects.all(),widget=forms.Select(attrs={'class': 'form-control'}))
    email = forms.EmailField(max_length=30, required=True,widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    ngo_name = forms.CharField(max_length=255,widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'NGO name'}))
    phone_no = forms.IntegerField(required=True,widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}))
    password1 = forms.CharField(max_length=150,widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'password'}))
    password2 = forms.CharField(max_length=150,widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'confirm password'}))
    class Meta(UserCreationForm.Meta):
        model = ngo
        fields = ('username','ngo_name', 'email','pincode', 'phone_no','latitude','longitude','password1', 'password2')
        widgets = {
            'username':TextInput(attrs={
                'class': "form-control",
                }),
            'email':EmailInput(attrs={
                'class': "form-control email-input",
                }),
            'phone_no': TextInput(attrs={
                'class': "form-control",
            }),
            'ngo_name': TextInput(attrs={
                'class': "form-control",
            }),
             'pincode': Select(attrs={
                'class': "form-control "
            }),
            'password1': PasswordInput(attrs={
                'class': "form-control password-input",
            }),
            'password2': PasswordInput(attrs={
                'class': "form-control password-input",
            }),
        
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }
   
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_ngo = True
        if commit:
            user.save()
        return user
    

'''
Same goes for which is used to customize the form for donor registration
''' 
class donorUserCreationForm(UserCreationForm):
    pincode = forms.ModelChoiceField(queryset=pincode.objects.all(),widget=forms.Select(attrs={'class': 'form-control'}))
    email = forms.EmailField(max_length=30, required=True,widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    donor_name = forms.CharField(max_length=255,widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Donor name'}))
    phone_no = forms.IntegerField(required=True,widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}))
    password1 = forms.CharField(max_length=150,widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'password'}))
    password2 = forms.CharField(max_length=150,widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'confirm password'}))
    class Meta(UserCreationForm.Meta):
        model = donor
        fields = ('username','donor_name','pincode', 'email', 'phone_no','latitude','longitude','password1', 'password2')
        widgets = {
           'username':TextInput(attrs={
                'class': "form-control",
                }),
            'email':EmailInput(attrs={
                'class': "form-control email-input",
                }),
            'phone_no': TextInput(attrs={
                'class': "form-control",
            }),
            'donor_name': TextInput(attrs={
                'class': "form-control",
            }),
             'pincode': Select(attrs={
                'class': "form-control "
            }),
            'password1': PasswordInput(attrs={
                'class': "form-control password-input",
            }),
            'password2': PasswordInput(attrs={
                'class': "form-control password-input",
            }),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_ngo = False
        if commit:
            user.save()
        return user
   
