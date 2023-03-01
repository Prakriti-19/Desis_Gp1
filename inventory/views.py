from rest_framework.viewsets import ReadOnlyModelViewSet
from .serializers import ngoSerializer,donorSerializer,donationsSerializer,locationSerializer
from .models import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from .forms import DonationForm
# from rest_framework.permissions import IsAuthenticated
# from .models import Image
# from .serializers import ImageSerializer
# from rest_flex_fields.views import FlexFieldsModelViewSet

# class ImageViewSet(FlexFieldsModelViewSet):

#     serializer_class = ImageSerializer
#     queryset = Image.objects.all()
#     permission_classes = [IsAuthenticated]


def donations_list(request):
    donat = donations.objects.all()
    return render(request, "inventory/donations_list", {'donations': donat})

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

class DonationView(LoginRequiredMixin, TemplateView):
    form_class = DonationForm
    template_name = "inventory/add_donation.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "HandsForHunger | Donate"
        return context

    def get(self, request):
        form = self.form_class()
        context = self.get_context_data()
        context["form"] = form
        return render(request, self.template_name, context)

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.instance.user = self.request.user
            form.save()
            return redirect("/")
        context = self.get_context_data()
        context.update({"form": form})
        return render(request, self.template_name, context)
    
