from django import forms
from django.contrib.auth.forms import UserCreationForm
from inventory.models import ngo,donor,pincode

class ngoUserCreationForm(UserCreationForm):
    pincode = forms.ModelChoiceField(queryset=pincode.objects.all())
    class Meta(UserCreationForm.Meta):
        model = ngo
        fields = ('username','ngo_name', 'email','pincode', 'phone_no','password1', 'password2')
    email = forms.CharField(max_length=30, required=True)
    ngo_name = forms.CharField(max_length=255)
    phone_no = forms.IntegerField(required=True)
   
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_ngo = True
        if commit:
            user.save()
        return user
    
class donorUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = donor
        fields = ('username','donor_name', 'email', 'phone_no','password1', 'password2')
    email = forms.CharField(max_length=30, required=True)
    phone_no = forms.IntegerField(required=True)
    donor_name = forms.CharField(max_length=255)
   
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_donor = True
        if commit:
            user.save()
        return user
   
