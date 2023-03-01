from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from inventory.models import ngo,donor

class ngoUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = ngo
        fields = ('username', 'email', 'phone_no','latitude','longitude','password1', 'password2')
    email = forms.CharField(max_length=30, required=True)
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
        fields = ('username', 'email', 'phone_no','points','latitude','longitude','password1', 'password2')
    email = forms.CharField(max_length=30, required=True)
    phone_no = forms.IntegerField(required=True)
    points = forms.IntegerField(required=True)
    longitude = forms.DecimalField(decimal_places=10,max_digits=15,required=True)
    latitude = forms.DecimalField(decimal_places=10,max_digits=15,required=True)
   
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_donor = True
        if commit:
            user.save()
        return user
   
