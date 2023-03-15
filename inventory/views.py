from django.http import HttpResponse
import matplotlib
matplotlib.use('Agg')
from rest_framework.viewsets import ReadOnlyModelViewSet
from .serializers import DonationSerializer
from inventory.models import *
import pandas as pd
from datetime import datetime, timedelta
from django.utils import timezone
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.db.models.functions import TruncMonth
from auth1.forms import *
from django.contrib.auth.decorators import login_required
import matplotlib.pyplot as plt
from django.db.models import Avg, Max, Min, Count, Sum, Q
import io
import base64

@login_required
def donate(request):
    if request.method == 'POST':
        form = DonationForm(request.POST, user=request.user)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.latitude = form.cleaned_data['latitude']
            donation.longitude = form.cleaned_data['longitude']
            donation.save()
            return redirect("donor_home")
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
                    points=points_to_redeem,
                    status=1
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
        redemption = Redemption.objects.create(
                    donor=donor_user,
                    points=points,
                    status=0)
        redemption.save()
        messages.success(request, f'{points} points donated to {ngo_user.ngo_name}')
        return redirect('donor_home')
    return render(request, 'inventory/donatep.html', {'ngos': ngos})

def donations_list(request):
    codes = request.GET.get('pincode')
    min_quantity = request.GET.get('min_quantity',0)
    max_quantity = request.GET.get('max_quantity',100)
    if codes is not None and min_quantity is not None and max_quantity is not None and min_quantity != '' and codes != ''and max_quantity != '':
        donation = donations.objects.filter( Q(pincode__code=codes) &  Q(quantity__range=(min_quantity, max_quantity)) & (Q(status=True) | Q(status2=True)))
    elif codes is not None  and  min_quantity != '' and codes == ''and max_quantity != '':
        donation = donations.objects.filter ( Q(pincode__code=request.user.pincode.code) & Q(quantity__range=(min_quantity, max_quantity)) &  (Q(status=True) | Q(status2=True)))
    elif codes is not None  and  min_quantity == '' and codes != ''and max_quantity == '':
        donation = donations.objects.filter( Q(pincode__code=codes) & Q(quantity__range=(0, 500)) & (Q(status=True) | Q(status2=True)))
    else:
        donation = donations.objects.filter(Q(status=True) | Q(status2=True))
    return render(request, "inventory/donations_list.html", {'donations': donation})

def donation_details(request, pk):
    donation = get_object_or_404(donations, pk=pk)
    return render(request, 'inventory/chat.html', {'donation': donation})

def update_points(donor_id, quantity, ngo_id):
    ngos = ngo.objects.get(id=ngo_id)
    donors = donor.objects.get(id=donor_id)
    donors.points += quantity
    ngos.points -= quantity
    donors.save()
    ngos.save()

def update_donation_status(request):
    if request.method == 'POST':
        donation_i = request.POST.get("donation_id")
        print(donation_i)
        try:
            donation = donations.objects.get(id=donation_i)
            print(donation.desc)
            donation.status = False
            donation.save()
            if donation.status== False and donation.status2 == False:
                update_points(donation.donor_id.id, donation.quantity,donation.ngo_id.id)
        except donations.DoesNotExist:
            # handle donation not found error
            return HttpResponse("Donation not found.")
        else:
            return redirect('donor_history')

def update_donation_status_ngo(request):
    if request.method == 'POST':
        donation_id = request.POST.get('donation_id2')
        try:
            donation = donations.objects.get(id=donation_id)
            donation.ngo_id=request.user
            donation.status2 = False
            donation.save()
            if donation.status== False and donation.status2 == False:
                update_points(donation.donor_id.id, donation.quantity,request.user.id)
        except donations.DoesNotExist:
            # handle donation not found error
            return HttpResponse("Donation not found.")
        else:
            return redirect('donations_list')

    
def donor_history(request):
    donor_instance = donor.objects.get(id=request.user.id)
    donations_made = donor_instance.donations_made()

    context = {
        'donor': donor_instance,
        'donations_made': donations_made,
    }

    return render(request, 'inventory/donor_history.html', context)

# class donationsViewSet(ReadOnlyModelViewSet):
#     serializer_class = DonationSerializer
#     queryset = donations.objects.all()

@login_required
def donations_stats(request):
    total_donations = donations.objects.count()
    avg_quantity = donations.objects.aggregate(Avg('quantity'))
    max_quantity = donations.objects.aggregate(Max('quantity'))
    total_quantity = donations.objects.aggregate(Sum('quantity'))
    avg_quantity =int(avg_quantity['quantity__avg'])
    context = {
        'total_donations': total_donations,
        'avg_quantity': avg_quantity,
        'max_quantity': max_quantity,
        'total_quantity': total_quantity
    }

# --------------------------------------------------------------------------------------------------------------------

    retention_period = timedelta(days=365)
    recent_donations = donations.objects.filter(donation_date__gt=datetime.now()-retention_period)
    returning_donors = {}
    for donation in recent_donations:
        month = donation.donation_date.replace(day=1)
        donor_id = donation.donor_id.id
        donors = donor.objects.filter(id=donor_id).first()
        if donor_id in returning_donors.get(month - retention_period, set()):
            continue
        if donors is not None and donations.objects.filter(donor_id=donor_id, donation_date__lt=month, donation_date__gt=month-retention_period).exists():
            returning_donors.setdefault(month, set()).add(donor_id)

    returning_donors = sorted(returning_donors.items())
    total_donors = donations.objects.count()

    retention_rates = [(month, len(returning)/total_donors*100) for month, returning in returning_donors]
    months = [month.strftime('%b %Y') for month, rate in retention_rates]
    rates = [rate for month, rate in retention_rates]
    buf = io.BytesIO()
    fig, ax = plt.subplots()
    ax.bar(months, rates)
    ax.set_ylabel('Returning donors (%)')
    ax.set_xlabel('Month')
    ax.set_title('Donor retention over time')
    plt.savefig(buf, format='png')
    buf.seek(0)
    plot_data2 = base64.b64encode(buf.getvalue()).decode('ascii')

# --------------------------------------------------------------------------------------------------------------------
    donations_by_month = donations.objects.annotate(month=TruncMonth('donation_date')).values('month') \
    .annotate(count=Count('id')) \
    .order_by('month')
    donation_counts = {d['month'].strftime('%b %Y'): d['count'] for d in donations_by_month}
    start_date = donations.objects.aggregate(Min('donation_date'))['donation_date__min']
    end_date = timezone.now().date()
    month_year = lambda d: d.strftime('%b %Y')
    months = [month_year(d) for d in pd.date_range(start_date, end_date, freq='MS')]
    donation_data = {}
    for month in months:
        if month in donation_counts:
            donation_data[month] = donation_counts[month]
        else:
            donation_data[month] = 0

    buf2 = io.BytesIO()
    fig, bx = plt.subplots()
    bx.bar(donation_data.keys(), donation_data.values())
    bx.set_ylabel('Number of Donations')
    bx.set_xlabel('Month')
    bx.set_title('Donations over last year')
    plt.xticks(rotation=45)
    plt.savefig(buf2, format='png')
    buf2.seek(0)
    plot_data = base64.b64encode(buf2.getvalue()).decode('ascii')

# ----------------------------------------------------------------------------------------------------------------------

    donations_by_pin = donations.objects.filter(pincode__code=request.user.pincode.code).annotate(month=TruncMonth('donation_date')).values('month') \
        .annotate(count=Count('id')) \
        .order_by('month')
    month = [d['month'].strftime('%b %Y') for d in donations_by_pin]
    donation_count = [d['count'] for d in donations_by_pin]

    buf3 = io.BytesIO()
    fig, cx = plt.subplots()
    cx.bar(month, donation_count)
    cx.set_ylabel('Number of Donations')
    cx.set_xlabel('Month')
    cx.set_title('Donations in your City')
    plt.savefig(buf3, format='png')
    buf3.seek(0)
    plot_data3 = base64.b64encode(buf3.getvalue()).decode('ascii')
    
# ----------------------------------------------------------------------------------------------------------------------

    total_donations = donations.objects.count()
    user_donations = donations.objects.filter( donor_id=request.user.id).count()
    percentage = round(user_donations / total_donations * 100, 2)
    labels = ['Your %', 'Others']
    sizes = [percentage, 100-percentage]
    colors = ['green', 'black']
    explode = (0.1, 0)
    plt.clf()
    plt.pie(sizes, explode=explode, labels=labels, colors=colors,
            autopct='%1.1f%%', startangle=90)

    plt.axis('equal')
    plt.title('Donations Percentage')
    plt.legend(title="Legend")
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image = base64.b64encode(buffer.getvalue()).decode('utf-8')
      

    homefood_count = donations.objects.filter(type='homefood').count()
    party_count = donations.objects.filter(type='party').count()
    restro_count = donations.objects.filter(type='restro').count()
    other_count = donations.objects.filter(type='other').count()
    # Create a bar graph
    types = ['Home Food', 'Party', 'Restro', 'Other']
    counts = [homefood_count, party_count, restro_count, other_count]
    buf4 = io.BytesIO()
    fig, dx = plt.subplots()
    dx.bar(types, counts)
    dx.set_title('Count of Each Type of Donation')
    dx.set_xlabel('Type of Donation')
    dx.set_ylabel('Count')
    plt.savefig(buf4, format='png')
    buf4.seek(0)
    plot_data4 = base64.b64encode(buf4.getvalue()).decode('ascii')
    
    return render(request, 'inventory/donations_stats.html', {'image': image,'plot_data': plot_data,'plot_data2': plot_data2,'plot_data3': plot_data3,'plot_data4': plot_data4, **context})


