from rest_framework.viewsets import ReadOnlyModelViewSet
from .serializers import ngoSerializer,donorSerializer,donationsSerializer,locationSerializer
from inventory.models import *
from inventory.models import pincode
from django.shortcuts import  get_object_or_404, redirect, render
from django.contrib import messages
from .forms import DonationForm, RedemptionForm
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

# @login_required
# def donations_stats(request):
#     total_donations = donations.objects.count()
#     avg_quantity = donations.objects.aggregate(Avg('quantity'))
#     max_quantity = donations.objects.aggregate(Max('quantity'))
#     min_quantity = donations.objects.aggregate(Min('quantity'))
#     # donations_by_donor = donations.objects.values(request.user.id).annotate(total_donations=Count(request.user.id))
#     # donations_by_pincode = donations.objects.values('pincode').annotate(total_donations=Count(248001))
#     # donations_by_month = donations.objects.annotate(year=ExtractYear('donation_date'),month=ExtractMonth('donation_date')).values('year', 'month').annotate(total_donations=Sum('quantity'))
#     # previous_year_donors = donations.objects.filter(donation_date__year=2022).values_list(request.user.id, flat=True).distinct()
#     # current_year_donors = donations.objects.filter(Q(donation_date__year=2023) & Q(donor_id__in=previous_year_donors)).values_list(request.user.id, flat=True).distinct()
#     # retention_rate = (current_year_donors.count() / previous_year_donors.count()) * 100

#     # center_point = Point(77.5946, 12.9716)
#     # radius = 5000
#     # donations_within_radius = donations.objects.annotate(
#     #     distance=Distance('point', center_point)
#     # ).filter(distance__lte=radius).aggregate(total_donations=Sum('quantity'))

   
#     # donor_names = [donor.name for donor in donor.objects.all()]
#     # donation_counts = [donation['total_donations'] for donation in donations_by_donor]

#     # fig, ax = plt.subplots()
#     # ax.bar(donor_names, donation_counts)
#     # ax.set_xlabel('Donor')
#     # ax.set_ylabel('Total Donations')
#     # ax.set_title('Donations by Donor')

#     # # Convert the Matplotlib figure to a PNG image
#     # from io import BytesIO
#     # import base64
#     # buffer = BytesIO()
#     # fig.savefig(buffer, format='png')
#     # buffer.seek(0)
#     # image_data = base64.b64encode(buffer.getvalue()).decode()
#     # plt.close()

#     context = {
#         'total_donations': total_donations,
#         'avg_quantity': avg_quantity,
#         'max_quantity': max_quantity,
#         'min_quantity': min_quantity,
#         # 'donations_by_donor': donations_by_donor,
#         # 'donations_by_pincode': donations_by_pincode,
#         # 'donations_by_month': donations_by_month,
#         # 'retention_rate': retention_rate,
#         # 'donations_within_radius': donations_within_radius,
#         # 'donor_chart': image_data
#     }

#     return render(request, 'donations_stats.html', context)



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


# def ngo_list(request):
#     ngos = ngo.objects.all()
#     context = {
#         'ngos': ngos
#     }
#     return render(request, 'ngo_list.html', context)

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