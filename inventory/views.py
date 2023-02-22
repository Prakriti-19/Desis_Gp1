from rest_framework.viewsets import ReadOnlyModelViewSet
from .serializers import ngoSerializer,donorSerializer,ImageSerializer
from .models import ngo,donor
from rest_framework.permissions import IsAuthenticated
from .models import Image
from .serializers import ImageSerializer
from rest_flex_fields.views import FlexFieldsModelViewSet

class ImageViewSet(FlexFieldsModelViewSet):

    serializer_class = ImageSerializer
    queryset = Image.objects.all()
    permission_classes = [IsAuthenticated]


class ngoViewSet(ReadOnlyModelViewSet):

    serializer_class = ngoSerializer
    queryset = ngo.objects.all()

class donorViewSet(ReadOnlyModelViewSet):

    serializer_class = donorSerializer
    queryset = donor.objects.all()