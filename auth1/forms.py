from django import forms
from django.contrib.auth.forms import UserCreationForm
from inventory.models import ngo,donor

class ngoUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = ngo
        fields = ('username','ngo_name', 'email', 'phone_no','latitude','longitude','password1', 'password2')
    email = forms.CharField(max_length=30, required=True)
    ngo_name = forms.CharField(max_length=255)
    phone_no = forms.IntegerField(required=True)
    longitude = forms.DecimalField(decimal_places=10,max_digits=15,required=True)
    latitude = forms.DecimalField(decimal_places=10,max_digits=15,required=True)
   
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_ngo = True
        if commit:
            user.save()
        return user
    
class donorUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = donor
        fields = ('username','donor_name', 'email', 'phone_no','latitude','longitude','password1', 'password2')
    email = forms.CharField(max_length=30, required=True)
    phone_no = forms.IntegerField(required=True)
    donor_name = forms.CharField(max_length=255)
    longitude = forms.DecimalField(decimal_places=10,max_digits=15,required=True)
    latitude = forms.DecimalField(decimal_places=10,max_digits=15,required=True)
   
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_donor = True
        if commit:
            user.save()
        return user
   
