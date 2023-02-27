from rest_framework.viewsets import ReadOnlyModelViewSet
from .serializers import ngoSerializer,donorSerializer,donationsSerializer,locationSerializer
from .models import *
# from rest_framework.permissions import IsAuthenticated
# from .models import Image
# from .serializers import ImageSerializer
# from rest_flex_fields.views import FlexFieldsModelViewSet

# class ImageViewSet(FlexFieldsModelViewSet):

#     serializer_class = ImageSerializer
#     queryset = Image.objects.all()
#     permission_classes = [IsAuthenticated]


class ngoViewSet(ReadOnlyModelViewSet):

    serializer_class = ngoSerializer
    queryset = ngo.objects.all()

class donationsViewSet(ReadOnlyModelViewSet):

    serializer_class = donationsSerializer
    queryset = donations.objects.all()

class locationViewSet(ReadOnlyModelViewSet):

    serializer_class = locationSerializer
    queryset = location.objects.all()

class donorViewSet(ReadOnlyModelViewSet):

    serializer_class = donorSerializer
    queryset = donor.objects.all()