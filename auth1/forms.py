from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import validate_email, RegexValidator
from inventory.models import ngo, donor, pincode, donations


class ngoUserCreationForm(UserCreationForm):
    '''
    The class ngoUserCreationForm is a subclass of the UserCreationForm provided by Django.
    The Meta class is used to provide additional metadata for the ngo model and is an example of abstraction. 
    '''
    pincode = forms.ModelChoiceField(required=True, queryset=pincode.objects.all(
    ), widget=forms.Select(attrs={'class': 'form-control', 'data-label': 'City'}), label="City")
    email = forms.EmailField(required=True, max_length=30, widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': 'Email'}), validators=[validate_email])
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    ngo_name = forms.CharField(required=True, max_length=255, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'NGO name'}))
    phone_no = forms.CharField(validators=[phone_regex], max_length=17, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Phone number'}))
    username = forms.CharField(max_length=255, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password1 = forms.CharField(required=True, max_length=150, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'data-label': 'Password', 'placeholder': 'Password'}), label='Password')
    password2 = forms.CharField(required=True, max_length=150, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'data-label': 'Confirm password', 'placeholder': 'confirm password'}), label='Confirm password')

    class Meta(UserCreationForm.Meta):
        model = ngo
        fields = ('username', 'ngo_name', 'email', 'pincode', 'phone_no',
                  'latitude', 'longitude', 'password1', 'password2')
        widgets = {
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }
        attrs = {
            'class': 'form-control',
        }

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        phone_no = cleaned_data.get('phone_no')
        if donor.objects.filter(email=email).exists():
            self.add_error('email', 'Email already exists.')
        if donor.objects.filter(phone_no=phone_no).exists():
            self.add_error('phone_no', 'Phone number already exists.')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_ngo = True
        if commit:
            user.save()
        return user


class donorUserCreationForm(UserCreationForm):
    '''
    Same goes for which is used to customize the form for donor registration
    '''
    pincode = forms.ModelChoiceField(queryset=pincode.objects.all(), widget=forms.Select(
        attrs={'class': 'form-control', 'data-label': 'City'}), label="City")
    email = forms.EmailField(max_length=30, required=True, widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': 'Email'}), validators=[validate_email])
    donor_name = forms.CharField(max_length=255, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Donor name'}))
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_no = forms.CharField(validators=[phone_regex], max_length=17, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Phone number'}))
    username = forms.CharField(max_length=255, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password1 = forms.CharField(max_length=150, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'data-label': 'Password', 'placeholder': 'Password'}), label='Password')
    password2 = forms.CharField(max_length=150, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'data-label': 'Confirm password', 'placeholder': 'confirm password'}), label='Confirm password')

    class Meta(UserCreationForm.Meta):
        model = donor
        fields = ('username', 'donor_name', 'pincode', 'email',
                  'phone_no', 'latitude', 'longitude', 'password1', 'password2')
        widgets = {
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }
        attrs = {
            'class': 'form-control',
        }
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        phone_no = cleaned_data.get('phone_no')
        if donor.objects.filter(email=email).exists():
            self.add_error('email', 'Email already exists.')
        if donor.objects.filter(phone_no=phone_no).exists():
            self.add_error('phone_no', 'Phone number already exists.')
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

    type = forms.TypedChoiceField(
        choices=TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        coerce=str,
    )
    pincode = forms.ModelChoiceField(
        queryset=pincode.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = donations
        fields = ('description', 'quantity', 'type', 'pincode',
                  'donation_date', 'exp_date', 'longitude', 'latitude')
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'No. of people it can serve'}),
            'donation_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'exp_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity <= 0:
            raise forms.ValidationError(
                'Quantity should be a positive integer')
        return quantity

    def save(self, commit=True):
        new_donation = super().save(commit=False)
        new_donation.donor_id = self.user
        if commit:
            new_donation.save()
        return new_donation


class RedemptionForm(forms.Form):
    points = forms.IntegerField(min_value=1)
