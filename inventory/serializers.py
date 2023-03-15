from datetime import date
from .models import donations
from rest_framework import serializers

# Used to validate the donation given by the user
class DonationSerializer(serializers.ModelSerializer):
    class Meta:
        model = donations
        fields = '__all__'

    def validate(self, data):
        # Check that the donation_date is not in the past
        donation_date = data.get('donation_date')
        if donation_date and donation_date < date.today():
            raise serializers.ValidationError("Donation date cannot be in the past.")
        
        # Check that the exp_date is not before the donation_date
        exp_date = data.get('exp_date')
        if donation_date and exp_date and exp_date < donation_date:
            raise serializers.ValidationError("Expiry date cannot be before the donation date.")
        
        # Check that the quantity is positive
        quantity = data.get('quantity')
        if quantity and quantity <= 0:
            raise serializers.ValidationError("Quantity must be positive.")
        
        return data

