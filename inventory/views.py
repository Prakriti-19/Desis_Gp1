from rest_framework.viewsets import ReadOnlyModelViewSet
from .serializers import ngoSerializer,donorSerializer,donationsSerializer,locationSerializer
from inventory.models import *
from inventory.models import pincode
from django.shortcuts import  redirect, render
from .forms import DonationForm
from django.contrib.auth.decorators import login_required


@login_required
def donate(request):
    if request.method == 'POST':
        form = DonationForm(request.POST, user=request.user)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.latitude = form.cleaned_data['latitude']
            donation.longitude = form.cleaned_data['longitude']
            donation.save()
            return redirect("home")
    else:
        form = DonationForm(user=request.user)
    return render(request, 'inventory/donate.html', {'form': form})


def donations_list(request):
    donate = donations.objects.all()
    return render(request, "inventory/donations_list.html", {'donations': donate})


class ngoViewSet(ReadOnlyModelViewSet):
    serializer_class = ngoSerializer
    queryset = ngo.objects.all()


class donationsViewSet(ReadOnlyModelViewSet):
    serializer_class = donationsSerializer
    queryset = donations.objects.all()


class locationViewSet(ReadOnlyModelViewSet):
    serializer_class = locationSerializer
    queryset = pincode.objects.all()


class donorViewSet(ReadOnlyModelViewSet):
    serializer_class = donorSerializer
    queryset = donor.objects.all()
