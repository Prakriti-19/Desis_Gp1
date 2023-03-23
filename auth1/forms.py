from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from inventory.models import ngo,donor,pincode,donations
from django.forms import PasswordInput, Select, TextInput, EmailInput, NumberInput

'''
The class ngoUserCreationForm is a subclass of the UserCreationForm provided by Django.
The Meta class is used to provide additional metadata for the ngo model and is an example of abstraction. 
'''
class ngoUserCreationForm(UserCreationForm):
    pincode = forms.ModelChoiceField(required=True,queryset=pincode.objects.all(),widget=forms.Select(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True,max_length=30,widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    ngo_name = forms.CharField(required=True,max_length=255,widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'NGO name'}))
    phone_no = forms.IntegerField(required=True,widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}))
    password1 = forms.CharField(required=True,max_length=150,widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'password'}))
    password2 = forms.CharField(required=True,max_length=150,widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'confirm password'}))
    class Meta(UserCreationForm.Meta):
        model = ngo
        fields = ('username','ngo_name', 'email','pincode', 'phone_no','latitude','longitude','password1', 'password2')
        widgets = {
            'username':TextInput(attrs={
                'class': "form-control",
                }),
            'email':EmailInput(attrs={
                'class': "form-control ",
                }),
            'phone_no': NumberInput(attrs={
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

    def clean_email(self):
        email = self.cleaned_data['email']
        if ngo.objects.filter(email=email).exists():
            raise ValidationError("Email already exists.")
        return email
   
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
    def clean_email(self):
        email = self.cleaned_data['email']
        if donor.objects.filter(email=email).exists():
            raise ValidationError("Email already exists.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_ngo = False
        if commit:
            user.save()
        return user

class DonationForm(forms.ModelForm):
    HOME_FOOD = 'homefood'
    PARTY = 'party'
    RESTAURANT = 'restro'
    OTHER = 'other'

    TYPE_CHOICES = [
        (HOME_FOOD, 'Home Food'),
        (PARTY, 'Party'),
        (RESTAURANT, 'Restaurant'),
        (OTHER, 'Other'),
    ]

    type = forms.ChoiceField(choices=TYPE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    pincode = forms.ModelChoiceField(queryset=pincode.objects.all(),widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = donations
        fields = ('desc','quantity','type','pincode','donation_date','exp_date', 'longitude','latitude')
        widgets = {
            'desc': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Description'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control','placeholder': 'No. of people it can serve'}),
            'donation_date': forms.DateInput(attrs={'class': 'form-control','placeholder': 'Donation date'}),
            'exp_date': forms.DateInput(attrs={'class': 'form-control','placeholder': 'Use-by Date'}),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        donation = super().save(commit=False)
        donation.donor_id = self.user
        if commit:
            donation.save()
        return donation
    
class RedemptionForm(forms.Form):
    points = forms.IntegerField(min_value=1)
   
