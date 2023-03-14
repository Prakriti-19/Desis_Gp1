from django import forms
from .models import donations,pincode


class DonationForm(forms.ModelForm):
    pincode = forms.ModelChoiceField(queryset=pincode.objects.all())
    class Meta:
        model = donations
        fields = ('desc','quantity','pincode','donation_date','exp_date', 'longitude','latitude')
        widgets = {

            '__all__': forms.TextInput(attrs={'class': 'my-form-class'}),
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
