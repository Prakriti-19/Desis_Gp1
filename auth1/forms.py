from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from auth1.constants import *
from inventory.constants import *
from inventory.models import *


class ngoUserCreationForm(UserCreationForm):
    """
    Form for creating a new NGO account. It is subclass of the UserCreationForm
    """

    pincode = forms.ModelChoiceField(
        required=True,
        queryset=Pincode.objects.all(),
        widget=forms.Select(attrs={"class": CONTROL, "data-label": "City"}),
        label="City",
    )
    email = forms.EmailField(
        required=True,
        max_length=MAX_LENGTH,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Email"}
        ),
    )
    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{9,15}$",
        message=PHONE_VAL,
    )
    ngo_name = forms.CharField(
        required=True,
        max_length=MAX_LENGTH,
        widget=forms.TextInput(attrs={"class": CONTROL, "placeholder": "NGO name"}),
    )
    phone_no = forms.CharField(
        validators=[phone_regex],
        max_length=SMALL_MAX_LENGTH,
        widget=forms.TextInput(attrs={"class": CONTROL, "placeholder": "Phone number"}),
    )
    username = forms.CharField(
        max_length=MAX_LENGTH,
        widget=forms.TextInput(attrs={"class": CONTROL, "placeholder": "Username"}),
    )
    password1 = forms.CharField(
        required=True,
        max_length=PASSWORD_LEN,
        widget=forms.PasswordInput(
            attrs={
                "class": CONTROL,
                "data-label": PASSWORD,
                "placeholder": PASSWORD,
            }
        ),
        label=PASSWORD,
    )
    password2 = forms.CharField(
        required=True,
        max_length=PASSWORD_LEN,
        widget=forms.PasswordInput(
            attrs={
                "class": CONTROL,
                "data-label": "Confirm password",
                "placeholder": "confirm password",
            }
        ),
        label="Confirm password",
    )

    class Meta(UserCreationForm.Meta):
        model = Ngo
        fields = (
            "username",
            "ngo_name",
            "email",
            "pincode",
            "phone_no",
            "latitude",
            "longitude",
            "password1",
            "password2",
        )
        widgets = {
            "latitude": forms.HiddenInput(),
            "longitude": forms.HiddenInput(),
        }
        attrs = {
            "class": "form-control",
        }

    def clean(self):
        """
        Overrides clean() method to add custom validation for email and phone
        number

        :return:
            error message in case of duplicacy in mail or phone number
        """
        cleaned_data = super().clean()
        email = cleaned_data.get(EMAIL)
        phone_no = cleaned_data.get(PHONE_NO)
        if Donor.objects.filter(email=email).exists():
            self.add_error(EMAIL, VALIDATION_MSG)
        if Donor.objects.filter(phone_no=phone_no).exists():
            self.add_error(PHONE_NO, VALIDATION_MSG)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_ngo = True
        if commit:
            user.save()
        return user


class donorUserCreationForm(UserCreationForm):
    """
    Form for creating a new Donor account. It is subclass of the
    UserCreationForm
    """

    pincode = forms.ModelChoiceField(
        queryset=Pincode.objects.all(),
        widget=forms.Select(attrs={"class": CONTROL, "data-label": "City"}),
        label="City",
    )
    email = forms.EmailField(
        max_length=MAX_LENGTH,
        required=True,
        widget=forms.EmailInput(attrs={"class": CONTROL, "placeholder": "Email"}),
    )
    donor_name = forms.CharField(
        max_length=MAX_LENGTH,
        widget=forms.TextInput(attrs={"class": CONTROL, "placeholder": "Donor name"}),
    )
    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{9,15}$",
        message=PHONE_VAL,
    )
    phone_no = forms.CharField(
        validators=[phone_regex],
        max_length=SMALL_MAX_LENGTH,
        widget=forms.TextInput(attrs={"class": CONTROL, "placeholder": "Phone number"}),
    )
    username = forms.CharField(
        max_length=MAX_LENGTH,
        widget=forms.TextInput(attrs={"class": CONTROL, "placeholder": "Username"}),
    )
    password1 = forms.CharField(
        max_length=PASSWORD_LEN,
        widget=forms.PasswordInput(
            attrs={
                "class": CONTROL,
                "data-label": PASSWORD,
                "placeholder": PASSWORD,
            }
        ),
        label=PASSWORD,
    )
    password2 = forms.CharField(
        max_length=PASSWORD_LEN,
        widget=forms.PasswordInput(
            attrs={
                "class": CONTROL,
                "data-label": "Confirm password",
                "placeholder": "confirm password",
            }
        ),
        label="Confirm password",
    )

    class Meta(UserCreationForm.Meta):
        model = Donor
        fields = (
            "username",
            "donor_name",
            "pincode",
            "email",
            "phone_no",
            "latitude",
            "longitude",
            "password1",
            "password2",
        )
        widgets = {
            "latitude": forms.HiddenInput(),
            "longitude": forms.HiddenInput(),
        }
        attrs = {
            "class": CONTROL,
        }

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get(EMAIL)
        phone_no = cleaned_data.get(PHONE_NO)
        if Donor.objects.filter(email=email).exists():
            self.add_error(EMAIL, VALIDATION_MSG)
        if Donor.objects.filter(phone_no=phone_no).exists():
            self.add_error(PHONE_NO, VALIDATION_MSG)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_ngo = False
        if commit:
            user.save()
        return user


class DonationForm(forms.ModelForm):
    """
    Form for creating a new Donation
    """

    TYPE_CHOICES = [
        (HOME_FOOD, "Home Food"),
        (PARTY, "Party"),
        (RESTAURANT, "Restaurant"),
        (OTHER, "Other"),
    ]

    type = forms.TypedChoiceField(
        choices=TYPE_CHOICES,
        widget=forms.Select(attrs={"class": CONTROL}),
        coerce=str,
    )
    pincode = forms.ModelChoiceField(
        queryset=Pincode.objects.all(),
        widget=forms.Select(attrs={"class": CONTROL}),
    )

    class Meta:
        model = Donations
        fields = (
            "description",
            "quantity",
            "type",
            "pincode",
            "donation_date",
            "exp_date",
            "longitude",
            "latitude",
        )
        widgets = {
            "description": forms.TextInput(
                attrs={"class": CONTROL, "placeholder": "Description"}
            ),
            "quantity": forms.NumberInput(
                attrs={
                    "class": CONTROL,
                    "placeholder": "No. of people it can serve",
                }
            ),
            "donation_date": forms.DateInput(attrs={"class": CONTROL, "type": "date"}),
            "exp_date": forms.DateInput(attrs={"class": CONTROL, "type": "date"}),
            "latitude": forms.HiddenInput(),
            "longitude": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

    def clean_quantity(self):
        quantity = self.cleaned_data[QUANTITY]
        if quantity <= 0:
            raise forms.ValidationError(QUANTITY_ERROR_MSG)
        return quantity

    def save(self, commit=True):
        new_donation = super().save(commit=False)
        new_donation.donor_id = self.user
        if commit:
            new_donation.save()
        return new_donation


class RedemptionForm(forms.Form):
    points = forms.IntegerField(min_value=1)
