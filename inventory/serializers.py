from .models import ngo,donor,donations,pincode
from rest_framework import serializers

class donorSerializer(serializers.ModelSerializer):
    class Meta:
        model = donor
        fields = '__all__'

class donationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = donations
        fields = '__all__' 

class locationSerializer(serializers.ModelSerializer):
    class Meta:
        model = pincode
        fields = '__all__' 
        

class ngoSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = ngo
        fields = '__all__' 
       