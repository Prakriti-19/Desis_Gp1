from .models import ngo,donor
from rest_framework import serializers
from .models import Image
from versatileimagefield.serializers import VersatileImageFieldSerializer
from rest_flex_fields import FlexFieldsModelSerializer

class ImageSerializer(FlexFieldsModelSerializer):
    image = VersatileImageFieldSerializer(
        sizes='product_headshot'
    )

    class Meta:
        model = Image
        fields = ['pk', 'name', 'image']

class donorSerializer(serializers.ModelSerializer):
    class Meta:
        model = donor
        fields = '__all__' 
        

class ngoSerializer(serializers.ModelSerializer):
    # category = CategorySerializer(many=True)
    
    class Meta:
        model = ngo
        fields = '__all__' 
        expandable_fields = {
            'image': ('reviews.ImageSerializer', {'many': True}),
        }