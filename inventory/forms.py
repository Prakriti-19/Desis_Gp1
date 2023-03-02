from django import forms
from .models import donations


class DonationForm(forms.ModelForm):
    class Meta:
        model = donations
        fields = ('exp_date', 'quantity', 'desc')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        donation = super().save(commit=False)
        donation.donor_id = self.user
        if commit:
            donation.save()
        return donation
