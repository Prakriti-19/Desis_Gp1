from django import forms
from .models import donations

class DonationForm(forms.ModelForm):
    desc = forms.Field(
        required=True,
        label="Description",
        widget=forms.Textarea(
            attrs={"class": "form-control", "placeholder": "Add some details.."}
        ),
    )
    exp_date = forms.DateField(
        required = True,
        label = "UsedBy_Date",
        widget = forms.DateInput(attrs={"class": "form-control", "type": "date"})
    )
    quantity = forms.IntegerField(
        required=True,
        label="Quantity",
        widget=forms.NumberInput(attrs={"class": "form-control", "type": "Integer"}),
    )

    class Meta:
        model = donations
        fields = ["desc", "quantity", "exp_date"]