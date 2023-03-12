from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.core.validators import validate_email,EmailValidator
from inventory.models import ngo,donor,pincode

class ngoUserCreationForm(UserCreationForm):
    pincode = forms.ModelChoiceField(queryset=pincode.objects.all())
    class Meta(UserCreationForm.Meta):
        model = ngo
        fields = ('username','ngo_name', 'email','pincode', 'phone_no','latitude','longitude','password1', 'password2')
        widgets = {
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }
    email = forms.EmailField(max_length=30, required=True)
    ngo_name = forms.CharField(max_length=255)
    phone_no = forms.IntegerField(required=True)

    def clean_email(self):
        email = self.cleaned_data['email']
        if ngo.objects.filter(email=email).exists():
            raise ValidationError("Email already exists.")
        if not validate_email(email):
            raise ValidationError("Invalid email format.")
        return email
   
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_ngo = True
        if commit:
            user.save()
        return user
    
class donorUserCreationForm(UserCreationForm):
    pincode = forms.ModelChoiceField(queryset=pincode.objects.all())
    class Meta(UserCreationForm.Meta):
        model = donor
        fields = ('username','donor_name','pincode', 'email', 'phone_no','latitude','longitude','password1', 'password2')
        widgets = {
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }
    email = forms.EmailField(max_length=30, required=True)
    phone_no = forms.IntegerField(required=True)
    donor_name = forms.CharField(max_length=255)

    def clean_email(self):
        email = self.cleaned_data['email']
        if donor.objects.filter(email=email).exists():
            raise ValidationError("Email already exists.")
        if not validate_email(email):
            raise ValidationError("Invalid email format.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_donor = True
        if commit:
            user.save()
        return user
   
