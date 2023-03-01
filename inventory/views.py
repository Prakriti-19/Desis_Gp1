from rest_framework.viewsets import ReadOnlyModelViewSet
from .serializers import ngoSerializer,donorSerializer,donationsSerializer,locationSerializer
from .models import *
from django.shortcuts import  redirect, render
from django.views.generic import TemplateView
from .forms import DonationForm
from django.contrib.auth.decorators import login_required


@login_required
def donate(request):
    if request.method == 'POST':
        form = DonationForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect("home")
    else:
        form = DonationForm(user=request.user)
    return render(request, 'donate.html', {'form': form})

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
