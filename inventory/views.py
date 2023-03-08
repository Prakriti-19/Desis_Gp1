from django.http import HttpResponse
from rest_framework.viewsets import ReadOnlyModelViewSet
from .serializers import ngoSerializer,donorSerializer,donationsSerializer,locationSerializer
from inventory.models import *
from inventory.models import pincode
from datetime import datetime, timedelta
from django.shortcuts import redirect, render, get_object_or_404
import matplotlib.pyplot as plt
from django.contrib import messages
from django.db.models.functions import TruncMonth
from .forms import DonationForm, RedemptionForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import matplotlib.pyplot as plt
from django.db.models import Avg, Max, Min, Count, Sum
from .models import donations
import io
import base64
from django.db.models import Q
@login_required
def donate(request):
    if request.method == 'POST':
        form = DonationForm(request.POST, user=request.user)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.latitude = form.cleaned_data['latitude']
            donation.longitude = form.cleaned_data['longitude']
            donation.save()
            donations.update_points(request.user.id, donation.quantity)
            return redirect("home")
    else:
        form = DonationForm(user=request.user)
    return render(request, 'inventory/donate.html', {'form': form})

@login_required
def redeem_points(request):
    if request.method == 'POST':
        form = RedemptionForm(request.POST)
        if form.is_valid():
            points_to_redeem = form.cleaned_data['points']
            donor = request.user
            if donor.points >= points_to_redeem:
                donor.points -= points_to_redeem
                donor.save()
                redemption = Redemption.objects.create(
                    donor=donor,
                    points=points_to_redeem
                )
                redemption.save()
                return redirect('redeem_success')
            else:
                form.add_error('points', 'You do not have enough points to redeem.')
    else:
        form = RedemptionForm()
    return render(request, 'inventory/redeem_points.html', {'form': form})

def redeem_success(request):
    return render(request, 'inventory/redeem_success.html')


@login_required
def donate_points(request):
    ngos = ngo.objects.all()
    if request.method == 'POST':
        selected_ngo = request.POST.get('ngo')
        points = int(request.POST.get('points'))
        if points <= 0:
            messages.error(request, 'Points should be greater than zero')
            return render(request, 'inventory/donatep.html', {'ngos': ngos})
        donor_user = donor.objects.get(id=request.user.id)
        ngo_user = ngo.objects.get(id=selected_ngo)
        if donor_user.points < points:
            messages.error(request, 'Not enough points to donate')
            return render(request, 'inventory/donatep.html', {'ngos': ngos})
        donor_user.points -= points
        donor_user.save()
        ngo_user.points += points
        ngo_user.save()
        messages.success(request, f'{points} points donated to {ngo_user.ngo_name}')
        return redirect('home')
    return render(request, 'inventory/donatep.html', {'ngos': ngos})

def donations_list(request):
    codes = request.GET.get('pincode')
    min_quantity = request.GET.get('min_quantity',0)
    max_quantity = request.GET.get('max_quantity',100)
    if codes is not None and min_quantity is not None and max_quantity is not None and min_quantity != '' and codes != ''and max_quantity != '':
        donation = donations.objects.filter(pincode__code=codes, 
                                        quantity__range=(min_quantity, max_quantity),status=True)
    elif codes is not None  and  min_quantity != '' and codes == ''and max_quantity != '':
        donation = donations.objects.filter(pincode__code=request.user.pincode.code, 
                                        quantity__range=(min_quantity, max_quantity),status=True)
    elif codes is not None  and  min_quantity == '' and codes != ''and max_quantity == '':
        donation = donations.objects.filter(pincode__code=codes, 
                                        quantity__range=(0, 500),status=True)
    else:
        donation = donations.objects.filter(status=True)
    return render(request, "inventory/donations_list.html", {'donations': donation})

def donation_details(request, pk):
    donation = get_object_or_404(donations, pk=pk)
    return render(request, 'inventory/chat.html', {'donation': donation})

def update_points(donor_id, quantity):
    donors = donor.objects.get(id=donor_id)
    donors.points += quantity
    donors.save()

def update_donation_status(request):
    if request.method == 'POST':
        donation_id = request.POST.get('donation_id')
        status_str = request.POST.get('status')
        status = True if status_str.lower() == 'true' else False
        try:
            donation = donations.objects.get(id=donation_id)
            donation.status = status
            donation.save()
            update_points(donation.donor_id.id, donation.quantity)
        except donations.DoesNotExist:
            # handle donation not found error
            return HttpResponse("Donation not found.")
        else:
            return redirect('donor_history')

    
def donor_history(request):
    donor_instance = donor.objects.get(id=request.user.id)
    donations_made = donor_instance.donations_made()

    context = {
        'donor': donor_instance,
        'donations_made': donations_made,
    }

    return render(request, 'inventory/donor_history.html', context)

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

@login_required
def donations_stats(request):
    total_donations = donations.objects.count()
    avg_quantity = donations.objects.aggregate(Avg('quantity'))
    max_quantity = donations.objects.aggregate(Max('quantity'))
    min_quantity = donations.objects.aggregate(Min('quantity'))
    context = {
        'total_donations': total_donations,
        'avg_quantity': avg_quantity,
        'max_quantity': max_quantity,
        'min_quantity': min_quantity
    }
    
    retention_period = timedelta(days=365)
    recent_donations = donations.objects.filter(donation_date__gt=datetime.now()-retention_period)
    returning_donors = {}
    for donation in recent_donations:
        month = donation.donation_date.replace(day=1)
        donors_id = donation.donor_id.id
        donors = donor.objects.filter(id=donors_id).first()
        if donors_id in returning_donors.get(month - retention_period, set()):
            continue
        if donors is not None and donations.objects.filter(donor_id=donors_id, donation_date__lt=month, donation_date__gt=month-retention_period).exists():
            returning_donors.setdefault(month, set()).add(donors_id)

    # Sort the dictionary by month and convert it to a list of (month, percentage) tuples
    returning_donors = sorted(returning_donors.items())
    total_donors = set(donations.objects.values_list('id', flat=True).distinct())
    retention_rates = [(month, len(returning)/len(total_donors)*100) for month, returning in returning_donors]

    # Create the line chart
    months = [month.strftime('%b %Y') for month, rate in retention_rates]
    rates = [rate for month, rate in retention_rates]
    for r in retention_rates:
        print("Ferf")
        print(r)
    plt.plot(months, rates)
    plt.xlabel('Month')
    plt.ylabel('Returning donors (%)')
    plt.title('Donor retention over time')
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plot_data2 = base64.b64encode(buf.getvalue()).decode('ascii')

    donations_by_month = donations.objects.annotate(month=TruncMonth('donation_date')) \
        .values('month') \
        .annotate(count=Count('id')) \
        .order_by('month')

    # convert queryset to lists for plotting
    months = [d['month'].strftime('%b %Y') for d in donations_by_month]
    donation_counts = [d['count'] for d in donations_by_month]

    fig, ax = plt.subplots()
    ax.bar(months, donation_counts)
    ax.set_ylabel('Number of Donations')
    ax.set_xlabel('Month')
    ax.set_title('Donations per Month')

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plot_data = base64.b64encode(buf.getvalue()).decode('ascii')
    return render(request, 'inventory/donations_stats.html', {'plot_data': plot_data,'plot_data2': plot_data2, **context})
   

