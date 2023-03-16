from django.http import HttpResponse
import matplotlib
matplotlib.use('Agg')
from inventory.models import *
from django.contrib.auth import get_user_model
from dateutil.relativedelta import relativedelta
import numpy as np
from datetime import datetime, timedelta, date
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.db.models.functions import TruncMonth
from auth1.forms import *
from django.contrib.auth.decorators import login_required
import matplotlib.pyplot as plt
from django.db.models import Avg, Max,Sum, Q
import calendar
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
    donors.points += 5*quantity
    ngos.points -= 5*quantity
    donors.save()
    ngos.save()

def update_donation_status(request):
    if request.method == 'POST':
        donation_i = request.POST.get("donation_id")
        print(donation_i)
        try:
            donation = donations.objects.get(id=donation_i)
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


@login_required
def donations_stats(request): 
    User = get_user_model()
    ngo_count = User.objects.filter(is_ngo=True).count()
    donor_count = User.objects.filter(is_ngo=False).count()
    total_donations = donations.objects.count()
    avg_quantity = donations.objects.aggregate(Avg('quantity'))
    max_quantity = donations.objects.aggregate(Max('quantity'))
    total_quantity = donations.objects.aggregate(Sum('quantity'))
    avg_quantity =int(avg_quantity['quantity__avg'])

    context = {
        'ngo_count':ngo_count,
        'donor_count':donor_count,
        'total_donations': total_donations,
        'avg_quantity': avg_quantity,
        'max_quantity': max_quantity,
        'total_quantity': total_quantity
    }

# --------------------------------------------------------------------------------------------------------------------
    '''
    Calculating Donors Retention rate
    '''
    retention_period = timedelta(days=365)
    start_date = (datetime.now() - retention_period).replace(day=1)
    total_donors = donations.objects.count()
    end_date = datetime.now().replace(day=1)

    # Create a list of all months within the retention period
    all_months = []
    while start_date <= end_date:
        all_months.append(start_date)
        start_date += relativedelta(months=1)

    returning_donors = {}
    for donation in donations.objects.filter(donation_date__gt=datetime.now()-retention_period):
        month = donation.donation_date.replace(day=1)
        donor_id = donation.donor_id.id
        donors = donor.objects.filter(id=donor_id).first()
        if donor_id in returning_donors.get(month - retention_period, set()):
            continue
        if donors is not None and donations.objects.filter(donor_id=donor_id, donation_date__lt=month, donation_date__gt=month-retention_period).exists():
            returning_donors.setdefault(month, set()).add(donor_id)

    returning_donors = sorted(returning_donors.items())

    # Create a dictionary with all months as keys, and 0 as the initial value
    retention_dict = {}
    for month in all_months:
        retention_dict[month] = 0

    # Update the retention dictionary with the actual retention rates
    for month, returning in returning_donors:
        retention_dict[month] = len(returning)/total_donors*100

    # Convert the retention dictionary into two lists (months and rates)
    months = [month.strftime('%b %Y') for month in retention_dict.keys()]
    rates = [rate for rate in retention_dict.values()]

    buf = io.BytesIO()
    fig, ax = plt.subplots()
    ax.bar(months, rates,color='orange')
    ax.set_ylabel('Returning donors (%)')
    ax.set_xlabel('Month')
    ax.set_title('Donor retention over time')
    plt.xticks(rotation=45,fontsize=7)
    plt.savefig(buf, format='png')
    buf.seek(0)
    plot_data1 = base64.b64encode(buf.getvalue()).decode('ascii')

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------
    '''
    Donations per month Distribution: Overall, User's city and User-specific 
    '''
    today = datetime.now()
    first_day_of_month = today.replace(day=1)

    # Create a list of all the months in the current year
    all_months = []
    for i in range(12):
        month = (first_day_of_month - timedelta(days=30*i)).strftime('%b %Y')
        all_months.append(month)

    # Query the database for the user's donations per month
    user_donations = list(donations.objects.filter(pincode__code=request.user.pincode.code, donor_id=request.user)
                        .annotate(month=TruncMonth('donation_date'))
                        .values('month')
                        .annotate(total_donations=Sum('quantity'))
                        .order_by('month'))

    # Query the database for the city's donations per month
    city_donations = list(donations.objects.filter(pincode__code=request.user.pincode.code)
                        .annotate(month=TruncMonth('donation_date'))
                        .values('month')
                        .annotate(total_donations=Sum('quantity'))
                        .order_by('month'))
    tot_donations = list(donations.objects
                        .annotate(month=TruncMonth('donation_date'))
                        .values('month')
                        .annotate(total_donations=Sum('quantity'))
                        .order_by('month'))

    # Create a dictionary with all the months and their corresponding donation amounts
    user_donation_dict = {month: 0 for month in all_months}
    city_donation_dict = {month: 0 for month in all_months}
    tot_donation_dict = {month: 0 for month in all_months}

    # Populate the dictionaries with the actual donation amounts
    for donation in user_donations:
        month_str = donation['month'].strftime('%b %Y')
        user_donation_dict[month_str] = donation['total_donations']
    for donation in city_donations:
        month_str = donation['month'].strftime('%b %Y')
        city_donation_dict[month_str] = donation['total_donations']
    for donation in tot_donations:
        month_str = donation['month'].strftime('%b %Y')
        tot_donation_dict[month_str] = donation['total_donations']

    # Convert the dictionaries to lists for plotting
    user_month = list(user_donation_dict.keys())
    user_donation_amounts = list(user_donation_dict.values())
    city_month = list(city_donation_dict.keys())
    city_donation_amounts = list(city_donation_dict.values())
    tot_month = list(tot_donation_dict.keys())
    tot_donation_amounts = list(tot_donation_dict.values())

    # Plot the donations per month
    fig, ax = plt.subplots()
    ax.plot(user_month, user_donation_amounts, label='Your Donations',color= 'orange')
    ax.plot(city_month, city_donation_amounts, label='City Donations',color= 'black')
    ax.plot(tot_month, tot_donation_amounts, label='Total Donations',color= 'yellow')
    ax.set_xlabel('Month')
    ax.set_ylabel('Donation Amount')
    ax.set_title('Donations per Month')
    ax.legend()
    plt.xticks(rotation=45,fontsize=7)
    # Save the plot to a PNG image
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    # Convert the PNG image to a base64 string for display on the web page
    plot_data2 = base64.b64encode(buf.getvalue()).decode('ascii')
        
# -------------------------------------------------------------------------------------------------------------------------------------------------------------------
    '''
    Calculating Donation ratio of user in his city
    '''
    # Calculates sum of the quantity field for donations and returns a dictionary with a key quantity__sum
    total_donations =donations.objects.aggregate(Sum('quantity'))['quantity__sum']
    user_donations = donations.objects.filter(donor_id=request.user.id).aggregate(Sum('quantity'))['quantity__sum']
    percentage = round(user_donations / total_donations * 100, 2)

    # Define the labels, sizes, colors and explosion for the pie chart
    labels = ['Your %', 'Others']
    sizes = [percentage, 100-percentage]
    colors = ['orange', 'yellow']
    explode = (0.1, 0)

    # Clear the current figure
    plt.clf()

    # Create a pie chart with the specified settings
    plt.pie(sizes, explode=explode, labels=labels, colors=colors,
            autopct='%1.1f%%', startangle=90)

    # Set the axis to be equal and add a title and legend to the chart
    plt.axis('equal')
    plt.title('Donation Percentage in Your City')
    plt.legend(title="Legend")

    # Save the chart as a png image and convert it to base64 encoding
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image = base64.b64encode(buffer.getvalue()).decode('utf-8')
      

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------

    '''
    Donation Type Distribution: Overall and User-specific
    '''

    # Count the donations for the current user
    user_homefood_count = donations.objects.filter(donor_id=request.user, type='homefood').aggregate(Sum('quantity'))['quantity__sum'] or 0
    user_party_count = donations.objects.filter(donor_id=request.user, type='party').aggregate(Sum('quantity'))['quantity__sum'] or 0
    user_restro_count = donations.objects.filter(donor_id=request.user, type='restro').aggregate(Sum('quantity'))['quantity__sum'] or 0
    user_other_count = donations.objects.filter(donor_id=request.user, type='other').aggregate(Sum('quantity'))['quantity__sum'] or 0

    # Count the overall donations
    overall_homefood_count = donations.objects.filter(type='homefood').aggregate(Sum('quantity'))['quantity__sum'] or 0
    overall_party_count = donations.objects.filter(type='party').aggregate(Sum('quantity'))['quantity__sum'] or 0
    overall_restro_count = donations.objects.filter(type='restro').aggregate(Sum('quantity'))['quantity__sum'] or 0
    overall_other_count = donations.objects.filter(type='other').aggregate(Sum('quantity'))['quantity__sum'] or 0

    # Create a bar graph
    types = ['Households', 'Parties', 'Restro', 'Others']
    user_counts = [user_homefood_count, user_party_count, user_restro_count, user_other_count]
    overall_counts = [overall_homefood_count, overall_party_count, overall_restro_count, overall_other_count]

    fig, ax = plt.subplots()
    ax.bar(types, user_counts, label='Your',color= 'orange')
    ax.bar(types, overall_counts, bottom=user_counts, label='Overall Donations',color= 'yellow')
    ax.set_title('Sources of food wastage')
    ax.set_xlabel('Sources')
    ax.set_ylabel('Quantity')
    ax.legend()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    # Convert the PNG image to a base64 string for display on the web page
    plot_data3 = base64.b64encode(buf.getvalue()).decode('ascii')

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # start_date = datetime.today() - timedelta(weeks=10)
    # end_date = date.today()
    # end_datetime = datetime.combine(end_date, datetime.min.time())
    # donors = donor.objects.get(donor_name=request.user.donor_name)
    # days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    # Donations = donations.objects.filter(donor_id=donors, donation_date__range=[start_date, end_datetime])
    # donation_data = {}
    # # donation_data = [{day: 0 for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']} for _ in range(10)]
    # for donatio in Donations:
    #     quantity = donatio.quantity
    #     week_offset = (end_date - donation.donation_date).days // 7
    #     day = donation.donation_date.strftime('%a')
    #     quantity = donation.quantity
    #     if week_offset < len(donation_data) and day in days:
    #         donation_data[week_offset][day] += quantity
    #     else:
    #         print("Invalid week offset or day")
    # donation_array = np.array([[donation_data[i][day] for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']] for i in range(7)])
    # x_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    # y_labels = ["Week 1", "Week 2", "Week 3", "Week 4", "Week 5", "Week 6", "Week 7","Week 8","Week 9","Week 10"]
    # cmap = plt.get_cmap('Oranges')
    # fig, ax = plt.subplots()
    # heatmap = ax.imshow(donation_array, cmap=cmap)
    # cbar = ax.figure.colorbar(heatmap, ax=ax)
    # ax.set_xticks(np.arange(len(x_labels)))
    # ax.set_yticks(np.arange(len(y_labels)))
    # ax.set_xticklabels(x_labels)
    # ax.set_yticklabels(y_labels)
    # plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    # ax.set_title("Donations by Day")
    # fig.tight_layout()
    # buf5 = io.BytesIO()
    # plt.savefig(buf5, format='png')
    # buf5.seek(0)
    # plot_data5 = base64.b64encode(buf5.getvalue()).decode('ascii')

    donation_array = [[0 for i in range(52)] for j in range(7)]
    for donation in donations.objects.all():
        donation_date = donation.donation_date
        week_num = donation_date.isocalendar()[1] - 1 
        day_num = donation_date.weekday()
        donation_amount = donation.quantity
        donation_array[day_num][week_num] += donation_amount
    y_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    fig, ax = plt.subplots(figsize=(16,3))
    heatmap = ax.imshow(donation_array, cmap='Oranges')
    for i in range(len(donation_array)):
        for j in range(len(donation_array[i])):
            rect = plt.Rectangle((j-0.5,i-0.5),1,1,linewidth=1,edgecolor='white',facecolor='none')
            ax.add_patch(rect)
    cbar = ax.figure.colorbar(heatmap, ax=ax)
    ax.set_yticks(np.arange(len(y_labels)))
    ax.set_yticklabels(y_labels)
    ax.set_xticks(np.arange(0, len(calendar.month_name[1:])*4, 4))
    ax.set_xticklabels(calendar.month_name[1:])
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    ax.set_title("Your Activity")
    fig.tight_layout()
    buf5 = io.BytesIO()
    plt.savefig(buf5, format='png')
    buf5.seek(0)
    plot_data5 = base64.b64encode(buf5.getvalue()).decode('ascii')
    
        
    return render(request, 'inventory/donations_stats.html', {'image': image,'plot_data2': plot_data2,'plot_data3': plot_data3,'plot_data1': plot_data1,'plot_data5': plot_data5, **context})


