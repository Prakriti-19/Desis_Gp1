from rest_framework.viewsets import ReadOnlyModelViewSet
from .serializers import ngoSerializer,donorSerializer,donationsSerializer,locationSerializer
from inventory.models import *
from inventory.models import pincode
from django.shortcuts import redirect, render, get_object_or_404
import matplotlib.pyplot as plt
from django.contrib import messages
from .forms import DonationForm, RedemptionForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models.functions import ExtractYear, ExtractMonth
from django.db.models import Avg, Max, Min, Count, Sum
from .models import donations
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

def donations_list(request):
    codes = request.GET.get('pincode')
    min_quantity = request.GET.get('min_quantity',0)
    max_quantity = request.GET.get('max_quantity',100)
    if codes is not None and min_quantity is not None and max_quantity is not None and min_quantity != '' and codes != ''and max_quantity != '':
        donation = donations.objects.filter(pincode__code=codes, 
                                        quantity__range=(min_quantity, max_quantity))
    elif codes is not None  and  min_quantity != '' and codes == ''and max_quantity != '':
        donation = donations.objects.filter(pincode__code=request.user.pincode.code, 
                                        quantity__range=(min_quantity, max_quantity))
    elif codes is not None  and  min_quantity == '' and codes != ''and max_quantity == '':
        donation = donations.objects.filter(pincode__code=codes, 
                                        quantity__range=(0, 500))
    else:
        donation = donations.objects.all()
    return render(request, "inventory/donations_list.html", {'donations': donation})

def donation_details(request, pk):
    donation = get_object_or_404(donations, pk=pk)
    return render(request, 'inventory/chat.html', {'donation': donation})

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

    # donations_by_month = donations.objects.annotate(year=ExtractYear('donation_date'),
    # month=ExtractMonth('donation_date')).values('year', 'month').annotate(total_donations=Sum('quantity'))
    # print(donations_by_month)

    previous_year_donors = donations.objects.filter(donation_date__year=2022).values_list('donor_id', flat=True).distinct()
    # print(previous_year_donors)
    current_year_donors = donations.objects.filter(Q(donation_date__year=2023) & Q(donor_id__in=previous_year_donors)).values_list('donor_id', flat=True).distinct()
    if(previous_year_donors.count() == 0):
        retention_rate = (current_year_donors.count() ) * 100
    else:
        retention_rate = (current_year_donors.count() / previous_year_donors.count()) * 100
    print(retention_rate)

    retention_rates = []
    for i in range(1, 13):
        prev_month_donations = previous_year_donors.filter(donation_date__month=i)
        curr_month_donations = current_year_donors.filter(donation_date__month=i)
        if prev_month_donations.exists():
            rate = (curr_month_donations.count() / prev_month_donations.count()) * 100
        else:
            rate = 0
            retention_rates.append(rate)
    donations_by_month = donations.objects.filter( donation_date__year=2023).values('donation_date__month').annotate(total_donations=Count('donor_id'))
    # for donation in donations_by_month:
    #     print(donation['donation_date__month'], donation['total_donations'])
    print(retention_rates)

    donations_by_donor = donations.objects.values('donor_id').annotate(total_donations=Count('donor_id'))
    donor_names = [donor.donor_name for donor in donor.objects.all()]
    donation_counts = [donation['total_donations'] for donation in donations_by_donor]
    fig, ax = plt.subplots()
    ax.bar(donor_names, donation_counts)
    ax.set_xlabel('Donor')
    ax.set_ylabel('Total Donations')
    ax.set_title('Donations by Donor')
    from io import BytesIO
    import base64
    # def save_plot_to_image(fig):
    #     buffer = io.BytesIO()
    #     fig.savefig(buffer, format='png')
    #     buffer.seek(0)
    #     plot_url = base64.b64encode(buffer.getvalue()).decode('utf-8')
    #     plt.close()
    

    context = {
        'total_donations': total_donations,
        'avg_quantity': avg_quantity,
        'max_quantity': max_quantity,
        'min_quantity': min_quantity,
        'donations_by_donor': donations_by_donor,
        # 'donations_by_pincode': donations_by_pincode,
        'donations_by_month': donations_by_month,
        # 'retention_rate': retention_rate,
        # 'donations_within_radius': donations_within_radius,
        # 'donor_chart': image_data
    }

    return render(request, 'inventory/donations_stats.html', context)


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