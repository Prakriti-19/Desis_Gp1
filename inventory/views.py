from django.shortcuts import redirect, render, redirect
from django.db.models import Avg, Max, Sum, Q
import base64
import io
import matplotlib.pyplot as plt
from django.contrib.auth.decorators import login_required
import networkx as nx
from auth1.forms import *
from django.db.models.functions import TruncMonth
from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils import timezone
from datetime import datetime as dt, timedelta
import numpy as np
from math import radians, sin, cos, sqrt, atan2
from dateutil.relativedelta import relativedelta
from inventory.models import *
from django.http import HttpResponse, HttpResponseBadRequest
import matplotlib

matplotlib.use("Agg")


@login_required  # decorator used to ensure only after logging in one can access this function
def donate(request):
    """
    - View function to handle the donation form submission.
    - It returns a template that's converted into donate food page
    """
    if request.method == "POST":
        form = DonationForm(request.POST, user=request.user)
        if form.is_valid():
            # Save the donation object to the database
            donation = form.save(commit=False)
            donation.latitude = form.cleaned_data["latitude"]
            donation.longitude = form.cleaned_data["longitude"]
            donation.save()
            # Redirect the user to their donor home page upon successful submission
            return redirect("donor_home")
    else:
        # Display the donation form to the user
        form = DonationForm(user=request.user)
    # Render the donate.html template with the donation form
    return render(request, "inventory/donate.html", {"form": form})


@login_required
def redeem_points(request):
    """
    View function to handle the redemption of descoins by a donor.
    """
    if request.method == "POST":
        # Get the number of descoins to redeem from the POST data
        descoins_to_redeem = int(request.POST.get("descoins"))
        donor = request.user
        # Check if the donor has enough descoins to redeem
        if donor.descoins >= descoins_to_redeem:
            # Deduct the redeemed descoins from the donor's account and save the donor object
            donor.descoins -= descoins_to_redeem
            donor.save()
            # Create a new transaction object to record the redemption and save it to the database
            Transaction.objects.create(
                sender = donor.id,
                receiver = None,
                descoins_transferred=descoins_to_redeem,
                type = D2U,
                timestamp = timezone.now(),
            )
            # Display a success message to the user
            messages.success(request, "DESCOINS redeemed successfully.")
        else:
            # Display an error message to the user if the donor does not have enough descoins to redeem
            messages.error(request, "You do not have enough DESCOINS to redeem.")
    # Render the redeem_points.html template with the current user's data
    return render(request, "inventory/redeem_points.html")


@login_required
def mail(request, email):
    """
    View function to render a donation email template with the provided donor email address.
    """
    # Create a context dictionary containing the donor email address
    context = {
        "donor_email": email,
    }
    # Render the donation_email.html template with the context dictionary
    return render(request, "inventory/donation_email.html", context)


@login_required
def donate_points(request, ngo_id):
    """
    View function to handle donation of DESCOINS to an NGO.
    """
    if request.method == "POST":
        descoins_to_donate = request.POST.get("descoins")
        if descoins_to_donate is not None and descoins_to_donate.strip() != "":
            # Convert input to integer
            descoins_to_donate = int(descoins_to_donate)
            donor = request.user
            ng = ngo.objects.get(id=ngo_id)
            if donor.descoins >= descoins_to_donate:
                # Update donor and NGO DESCOINS balances
                donor.descoins -= descoins_to_donate
                donor.save()
                ng.descoins += descoins_to_donate
                ng.save()
                # Create transaction record
                Transaction.objects.create(
                    sender = donor.id,
                    receiver = ngo_id,
                    descoins_transferred = descoins_to_donate,
                    type = D2N,
                    timestamp = timezone.now(),
                )
                messages.success(request, "Donation made successfully.")
            else:
                messages.warning(request, "Insufficient DESCOINS to donate.")
        else:
            messages.warning(request, "Please enter DESCOINS to be donated")
    # Get the NGO object associated with the given ID
    ng = ngo.objects.get(id=ngo_id)
    context = {"ngo": ng}
    # Render the donatep.html template with the NGO object in the context dictionary
    return render(request, "inventory/donatep.html", context)


@login_required
def process_payment(request):
    """
    This function is used to process the payment made by a user.

    Returns:
        If request method is POST and amount is valid, it returns a success page with the amount as context.
        If request method is not POST or amount is invalid, it returns a Bad Request HTTP response.

    Variables:
        - amount: the amount to be paid.
        - context: dictionary that contains amount as key-value pair to be passed to the success page.
    """
    if request.method == "POST":
        amount = request.POST.get("amount")
        if (amount is None) or (not amount.isdigit()):
            return HttpResponseBadRequest("Invalid amount")
        context = {"amount": amount}
        return render(request, "payment_success.html", context)
    else:
        return HttpResponseBadRequest("Invalid request")


@login_required
def donations_list(request):
    """
    Returns a list of donations that match the filters provided by the user.

    Returns:
        A rendered HTML page that displays a list of donations.

    Variables:
        - request: the HTTP request object.
        - codes: the pin code to filter donations by (optional).
        - min_quantity: the minimum quantity of items to filter donations by (optional).
        - max_quantity: the maximum quantity of items to filter donations by (optional).
        - now: the current date and time.
        - filter_distance: the maximum distance in kilometers to filter donations by (optional).
        - donation: the queryset of donations that match the filters.
        - user_latitude: the latitude of the user's location.
        - user_longitude: the longitude of the user's location.
        - ngo_latitude: the latitude of an NGO's location.
        - ngo_longitude: the longitude of an NGO's location.
        - distance: the distance in kilometers between the user and that NGO.
    """
    codes = request.GET.get("pincode")
    min_quantity = request.GET.get("min_quantity")
    if (min_quantity is None) or (min_quantity == ""):
        min_quantity = 0
    max_quantity = request.GET.get("max_quantity")
    if (max_quantity is None) or (max_quantity == ""):
        max_quantity = 10000
    now = timezone.now()
    filter_distance = request.GET.get("distance")
    if (filter_distance is None) or (filter_distance == ""):
        filter_distance = 6371
    if (codes is None) or (codes == ""):
        donation = donations.objects.filter(
            Q(exp_date__gt = now)
            & Q(quantity__range = (min_quantity, max_quantity))
            & (Q(ngo_status = True) | Q(donor_status = True))
        ).order_by("exp_date")
    else:
        donation = donations.objects.filter(
            Q(exp_date__gt = now)
            & Q(pincode__code = codes)
            & Q(quantity__range = (min_quantity, max_quantity))
            & (Q(ngo_status=True) | Q(donor_status=True))
        ).order_by("exp_date")
    distances = []
    user_latitude = request.user.latitude
    user_longitude = request.user.longitude
    for d in donation:
        ngo_latitude = d.latitude
        ngo_longitude = d.longitude
        distance = haversine(user_latitude, user_longitude, ngo_latitude, ngo_longitude)
        if float(distance) <= float(filter_distance):
            distances.append((d, round(distance, 2)))
    return render(request, "inventory/donations_list.html", {"distances": distances})


@login_required
def ngo_list(request):
    """
    This function is used to display the list of all NGOs in the system, along with their distance from the current user's location.

    Returns:
        A rendered HTML page containing a list of all the NGOs and their distance from the user's location.

    Variables:
        - ngos: queryset of all the ngo objects in the system.
        - user_latitude: the latitude of the current user's location.
        - user_longitude: the longitude of the current user's location.
        - ngo_latitude: the latitude of an NGO's location.
        - ngo_longitude: the longitude of an NGO's location.
        - distance: the distance between the current user's location and an NGO's location, calculated using the haversine formula.
        - context: dictionary that contains the queryset of ngos and their distances to be passed to the rendered HTML page.
    """
    ngos = ngo.objects.all()
    user_latitude = request.user.latitude
    user_longitude = request.user.longitude
    for ng in ngos:
        ngo_latitude = ng.latitude
        ngo_longitude = ng.longitude
        distance = haversine(user_latitude, user_longitude, ngo_latitude, ngo_longitude)
        ng.distance = round(distance, 2)

    context = {"ngos": ngos}
    return render(request, "inventory/ngo_list.html", context)


def haversine(lat1, lon1, lat2, lon2):
    """
    This function calculates the haversine distance between two geographical points on Earth.

    Args:
        - lat1: latitude of the first point.
        - lon1: longitude of the first point.
        - lat2: latitude of the second point.
        - lon2: longitude of the second point.

    Returns:
        - distance: the haversine distance between the two points in kilometers.

    Variables:
        - R: radius of Earth in kilometers.
        - lat1, lon1, lat2, lon2: latitudes and longitudes of the two points in radians.
        - dlat: difference between the latitudes of the two points in radians.
        - dlon: difference between the longitudes of the two points in radians.
        - a, c: intermediate values used in the calculation
        - distance: the haversine distance between the two points in kilometers.
    """
    R = 6371  # radius of Earth in kilometers
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance


@login_required
def update_donation_status_donor(request):
    """
    This function updates the status of a donation made by a donor to 'False', which confirms that the donation has been given to the ngo.

    Returns:
        - If request method is POST and donation_id is valid, it returns a redirect to the donor_history page.
        - If donation_id is invalid, it returns a 'Donation not found' HTTP response.

    Variables:
        - donation_id: the ID of the donation to be updated.
        - donation: the donation object retrieved from the database using the donation_id.
        - update_points(): a function that updates the points of the donor and NGO based on the quantity of the donation made by the donor.
    """
    if request.method == "POST":
        donation_i = request.POST.get("donation_id")
        try:
            donation = donations.objects.get(id=donation_i)
            donation.donor_status = False
            donation.save()
            if donation.donor_status == False and donation.ngo_status == False:
                update_points(
                    donation.donor_id.id, donation.quantity, donation.ngo_id.id
                )
        except donations.DoesNotExist:
            return HttpResponse("Donation not found.")
        else:
            return redirect("donor_history")


@login_required
def update_donation_status_ngo(request):
    """
    This function is used to update the status of a donation by an NGO, confirming that the donation is taken by the ngo

    Returns:
        If request method is POST and donation is found, it updates the status and redirects to donations_list page.
        If donation is not found, it returns an HTTP response stating "Donation not found".

    Variables:
        - donation_id: the id of the donation to be updated.
        - donation: the donation object to be updated.
    """
    if request.method == "POST":
        donation_id = request.POST.get("donation_id2")
        try:
            donation = donations.objects.get(id=donation_id)
            donation.ngo_id = request.user
            donation.ngo_status = False
            donation.save()
            if donation.donor_status == False and donation.ngo_status == False:
                update_points(donation.donor_id.id, donation.quantity, request.user.id)
        except donations.DoesNotExist:
            return HttpResponse("Donation not found.")
        else:
            return redirect("donations_list")


def update_points(donor_id, quantity, ngo_id):
    """
    This function updates the descoins of the donor and ngo after a donation is made.

    Args:
        - donor_id: ID of the donor.
        - quantity: Quantity of the donation.
        - ngo_id: ID of the ngo.

    Returns:
        None
    """
    ngos = ngo.objects.get(id=ngo_id)
    donors = donor.objects.get(id=donor_id)
    donors.descoins += 5 * quantity
    ngos.descoins -= 5 * quantity
    donors.save()
    ngos.save()
    Transaction.objects.create(
        sender = ngos.id,
        receiver = donors.id,
        descoins_transferred = 5 * quantity,
        type = N2D,
        timestamp = timezone.now(),
    )


@login_required
def donor_history(request):
    """
    This view displays the history of donations made by the currently logged-in donor.

    Returns:
        A HTML page that lists all the donations made by the donor, along with the details of the NGO and the status
        of the donation (pending or completed).

    Variables:
        - donor_instance: the instance of the currently logged-in donor.
        - donations_made: a queryset of all the donations made by the donor.
        - context: dictionary that contains the donor instance and the donations made queryset to be passed to the HTML page.
    """
    donor_instance = donor.objects.get(id=request.user.id)
    donations_made = donor_instance.donations_made()

    context = {
        "donor": donor_instance,
        "donations_made": donations_made,
    }
    return render(request, "inventory/donor_history.html", context)


@login_required
def donations_stats(request):
    '''
    This function handles all the statistical analysis done on the data
    '''

    # Retrieve all donations and donors
    all_donations = donations.objects.all()
    all_donors = donor.objects.all()

    # Filter donations made by the currently logged-in donor
    user_donation = all_donations.filter(donor_id=request.user.id)

    # Count the number of NGOs and donors
    ngo_count = ngo.objects.count()
    donor_count = donor.objects.filter(is_superuser=False).count()

    # Get statistics about donations
    total_donations = all_donations.count()
    avg_quantity = all_donations.aggregate(Avg("quantity"))
    max_quantity = all_donations.aggregate(Max("quantity"))
    total_quantity = all_donations.aggregate(Sum("quantity"))
    avg_quantity = int(avg_quantity["quantity__avg"])

    # Create context dictionary to pass variables to the HTML template
    context = {
        "ngo_count": ngo_count,
        "donor_count": donor_count,
        "total_donations": total_donations,
        "avg_quantity": avg_quantity,
        "max_quantity": max_quantity,
        "total_quantity": total_quantity,
    }

    # --------------------------------------------------------------------------------------------------------------------
    """
    Calculating Donors Retention rate
    """
    retention_period = timedelta(days=365)
    start_date = (dt.now() - retention_period).replace(day=1)
    end_date = dt.now().replace(day=1)
    all_months = []

    # Create a list of all the months in the retention period
    while start_date <= end_date:
        all_months.append(start_date)
        start_date += relativedelta(months=1)

    # Create a dictionary of returning donors for each month in the retention period
    returning_donors = {}

    # Loop through all the donations made in the retention period
    for donation in all_donations.filter(donation_date__gt=dt.now() - retention_period):
        # Get the month of the donation
        month = donation.donation_date.replace(day=1)

        # Get the donor ID of the donation
        donor_id = donation.donor_id.id

        # Get the donor instance of the donation
        donors = all_donors.filter(id=donor_id).first()

        # Check if the donor is already marked as a returning donor in this month
        if donor_id in returning_donors.get(month - retention_period, set()):
            continue

        # Check if the donor has made a donation in the previous retention period
        if ( (donors is not None)
            and (all_donations.filter(
                donor_id=donor_id,
                donation_date__lt=month,
                donation_date__gt=month - retention_period,
            ).exists())):
            # Mark the donor as a returning donor for this month
            returning_donors.setdefault(month, set()).add(donor_id)

    # Sort the returning donors by month
    returning_donors = sorted(returning_donors.items())

    # Create a dictionary to store the retention rates for each month
    retention_dict = {}
    for month in all_months:
        retention_dict[month] = 0

    # Update the retention dictionary with the actual retention rates
    for month, returning in returning_donors:
        # Calculate the retention rate as the number of returning donors divided by the total number of donors
        retention_rate = len(returning) / len(all_donors) * 100

        # Add the retention rate to the retention dictionary for this month
        retention_dict[month] = retention_rate

    # Convert the retention dictionary into two lists (months and rates)
    months = [month.strftime("%b %Y") for month in retention_dict.keys()]
    rates = [rate for rate in retention_dict.values()]

    buf = io.BytesIO()
    fig, ax = plt.subplots()
    ax.bar(months, rates, color="orange")
    ax.set_ylabel("Returning donors (%)")
    ax.set_xlabel("Month")
    ax.set_title("Donor retention over time")
    plt.xticks(rotation=45, fontsize=7)

    # Convert the PNG image to a base64 string for display on the web page
    plt.savefig(buf, format="png")
    buf.seek(0)
    plot_data1 = base64.b64encode(buf.getvalue()).decode("ascii")

    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------
    """
    Donations per month Distribution: Overall, User's city and User-specific 
    """
    today = dt.now()
    first_day_of_month = today.replace(day=1)

    # Create a list of all the months in the current year
    all_months = []
    for i in range(12):
        month = (first_day_of_month - timedelta(days=30 * i)).strftime("%b %Y")
        all_months.append(month)

    # Query the database for the user's donations per month
    user_donations = list(
        user_donation.filter(pincode__code=request.user.pincode.code)
        .annotate(month=TruncMonth("donation_date"))
        .values("month")
        .annotate(total_donations=Sum("quantity"))
        .order_by("month")
    )

    # Query the database for the city's donations per month
    city_donations = list(
        all_donations.filter(pincode__code=request.user.pincode.code)
        .annotate(month=TruncMonth("donation_date"))
        .values("month")
        .annotate(total_donations=Sum("quantity"))
        .order_by("month")
    )
    tot_donations = list(
        all_donations.annotate(month=TruncMonth("donation_date"))
        .values("month")
        .annotate(total_donations=Sum("quantity"))
        .order_by("month")
    )

    # Create a dictionary with all the months and their corresponding donation amounts
    user_donation_dict = {month: 0 for month in all_months}
    city_donation_dict = {month: 0 for month in all_months}
    tot_donation_dict = {month: 0 for month in all_months}

    # Populate the dictionaries with the actual donation amounts
    for donation in user_donations:
        month_str = donation["month"].strftime("%b %Y")
        user_donation_dict[month_str] = donation["total_donations"]
    for donation in city_donations:
        month_str = donation["month"].strftime("%b %Y")
        city_donation_dict[month_str] = donation["total_donations"]
    for donation in tot_donations:
        month_str = donation["month"].strftime("%b %Y")
        tot_donation_dict[month_str] = donation["total_donations"]

    # Convert the dictionaries to lists for plotting
    user_month = list(user_donation_dict.keys())
    user_donation_amounts = list(user_donation_dict.values())
    city_month = list(city_donation_dict.keys())
    city_donation_amounts = list(city_donation_dict.values())
    tot_month = list(tot_donation_dict.keys())
    tot_donation_amounts = list(tot_donation_dict.values())

    # Plot the donations per month
    fig, ax = plt.subplots()
    ax.plot(user_month, user_donation_amounts, label="Your Donations", color="orange")
    ax.plot(city_month, city_donation_amounts, label="City Donations", color="black")
    ax.plot(tot_month, tot_donation_amounts, label="Total Donations", color="yellow")
    ax.set_xlabel("Month")
    ax.set_ylabel("Donation Amount")
    ax.set_title("Donations per Month")
    ax.legend()
    plt.xticks(rotation=45, fontsize=7)

    # Save the plot to a PNG image
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)

    # Convert the PNG image to a base64 string for display on the web page
    plot_data2 = base64.b64encode(buf.getvalue()).decode("ascii")

    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------
    """
    Calculating Donation ratio of user in his city
    """
    # Calculates sum of the quantity field for donations and returns a dictionary with a key quantity__sum
    total_donations = all_donations.aggregate(Sum("quantity"))["quantity__sum"]
    user_donations = user_donation.aggregate(Sum("quantity"))["quantity__sum"]
    percentage = round(user_donations / total_donations * 100, 2)

    # Define the labels, sizes, colors and explosion for the pie chart
    labels = ["Your %", "Others"]
    sizes = [percentage, 100 - percentage]
    colors = ["orange", "yellow"]
    explode = (0.1, 0)

    # Clear the current figure
    plt.clf()

    # Create a pie chart with the specified settings
    plt.pie(
        sizes,
        explode=explode,
        labels=labels,
        colors=colors,
        autopct="%1.1f%%",
        startangle=90,
    )

    # Set the axis to be equal and add a title and legend to the chart
    plt.axis("equal")
    plt.title("Donation Percentage in Your City")
    plt.legend(title="Legend")

    # Convert the PNG image to a base64 string for display on the web page
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    image = base64.b64encode(buffer.getvalue()).decode("utf-8")

    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------

    """
    Donation Type Distribution: Overall and User-specific
    """
    # Get the user's donation counts
    user_homefood_count = (
        user_donation.filter(type="homefood").aggregate(Sum("quantity"))[
            "quantity__sum"
        ]
        or 0
    )
    user_party_count = (
        user_donation.filter(type="party").aggregate(Sum("quantity"))["quantity__sum"]
        or 0
    )
    user_restro_count = (
        user_donation.filter(type="restro").aggregate(Sum("quantity"))["quantity__sum"]
        or 0
    )
    user_other_count = (
        user_donation.filter(type="other").aggregate(Sum("quantity"))["quantity__sum"]
        or 0
    )

    # Get the overall donation counts
    overall_homefood_count = (
        all_donations.filter(type="homefood").aggregate(Sum("quantity"))[
            "quantity__sum"
        ]
        or 0
    )
    overall_party_count = (
        all_donations.filter(type="party").aggregate(Sum("quantity"))["quantity__sum"]
        or 0
    )
    overall_restro_count = (
        all_donations.filter(type="restro").aggregate(Sum("quantity"))["quantity__sum"]
        or 0
    )
    overall_other_count = (
        all_donations.filter(type="other").aggregate(Sum("quantity"))["quantity__sum"]
        or 0
    )

    # Create a bar graph
    types = ["Homefood", "Party", "Restro", "Other"]
    # x-coordinates for user bars
    user_x = [i - 0.175 for i in range(len(types))]
    # x-coordinates for overall bars
    overall_x = [i + 0.175 for i in range(len(types))]
    bar_width = 0.35
    fig, ax = plt.subplots()
    ax.bar(
        user_x,
        [user_homefood_count, user_party_count, user_restro_count, user_other_count],
        label="Your",
        color="orange",
        width=bar_width,
    )
    ax.bar(
        overall_x,
        [
            overall_homefood_count,
            overall_party_count,
            overall_restro_count,
            overall_other_count,
        ],
        label="Overall Donations",
        color="yellow",
        width=bar_width,
    )

    ax.set_title("Sources of food wastage")
    ax.set_xlabel("Sources")
    ax.set_ylabel("Quantity")
    ax.set_xticks(range(len(types)))
    ax.set_xticklabels(types)
    ax.legend()

    # Save the figure to a buffer in PNG format
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)

    # Convert the PNG image to a base64 string for display on the web page
    plot_data3 = base64.b64encode(buf.getvalue()).decode("ascii")

    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------
    """
    Creates a 2D array with current users donation on each day to be displayed as a grid
    """
    import datetime
    today = datetime.date.today()
    one_year_ago = datetime.date(today.year, 1, 1)
    date_list = [
        one_year_ago + datetime.timedelta(days=x)
        for x in range((today - one_year_ago).days + 1)
    ]
    donation_dict = {date.strftime("%Y-%m-%d"): 0 for date in date_list}
    for donation in user_donation:
        donation_date = donation.donation_date
        if one_year_ago <= donation_date <= today:
            donation_dict[donation_date.strftime("%Y-%m-%d")] += donation.quantity
    donation_array = [[0 for _ in range(7)] for _ in range(52)]
    for i, date in enumerate(date_list):
        week_num = date.isocalendar()[1] - 1
        day_num = date.weekday()
        donation_array[week_num][day_num] = donation_dict[date.strftime("%Y-%m-%d")]
    y_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    donation_array = np.transpose(donation_array)
    k = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec","Jan"]
    x_labels = []
    l = 0
    for i in range(0, 52):
        if i % 4 == 0:
            x_labels.append(k[l])
            l += 1
        else:
            x_labels.append("")
    fig, ax = plt.subplots(figsize=(16, 3))
    heatmap = ax.imshow(donation_array, cmap="Oranges")
    for i in range(len(donation_array)):
        for j in range(len(donation_array[i])):
            rect = plt.Rectangle(
                (j - 0.5, i - 0.5),
                1,
                1,
                linewidth=1,
                edgecolor="white",
                facecolor="none",
            )
            ax.add_patch(rect)
    cbar = ax.figure.colorbar(heatmap, ax=ax)
    ax.set_xticks(np.arange(len(x_labels)))
    ax.set_xticklabels(x_labels)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    ax.set_yticks(np.arange(len(y_labels)))
    ax.set_yticklabels(y_labels)
    ax.set_title("Your Activity")
    fig.tight_layout()
    buf5 = io.BytesIO()
    plt.savefig(buf5, format="png")
    buf5.seek(0)

    # Convert the PNG image to a base64 string for display on the web page
    plot_data5 = base64.b64encode(buf5.getvalue()).decode("ascii")

    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # # Get the transaction data
    # transactions = Transaction.objects.filter(
    #     sender=request.user).order_by('date')
    # prefix_sum = 0
    # daily_totals = []

    # for transaction in transactions:
    #     prefix_sum += transaction.descoins_transferred
    #     daily_totals.append(prefix_sum)
    # daily_totals.insert(0, 0)
    # dates = [transaction.date.strftime('%m/%d/%Y')
    #          for transaction in transactions]
    # dates.insert(0, '1/1/2020')

    # fig, ax = plt.subplots(figsize=(15, 6))  # set the figure size
    # ax.plot(dates, daily_totals, color='orange')
    # ax.set_xlabel('Transaction Date')
    # ax.set_ylabel('Coins')
    # ax.set_title('Transaction History')
    # ax.set_xticklabels(dates)

    # # Save the plot to a buffer and encode it as base64 for display in the HTML template
    # buffer9 = io.BytesIO()
    # plt.savefig(buffer9, format='png')
    # buffer9.seek(0)
    # plot_data6 = base64.b64encode(buffer9.getvalue()).decode('ascii')
    # plt.close()

    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Created a weighted graph with each node as the city and edge as the transaction
    # between the city having edge weight as the quantity of transaction
    graph = {}
    for donation in all_donations:
        if donation.ngo_id is not None:
            city1 = donation.donor_id.pincode.city
            city2 = donation.ngo_id.pincode.city
            amount = donation.quantity
            if city1 not in graph:
                graph[city1] = {}
            if city2 not in graph:
                graph[city2] = {}
            graph[city1][city2] = amount
            graph[city2][city1] = amount

    G = nx.DiGraph()
    for city1 in graph:
        for city2 in graph[city1]:
            amount = graph[city1][city2]
            G.add_edge(city1, city2, weight=amount)
    total_edges = G.number_of_edges()
    total_weight = sum([G.edges[edge]["weight"] for edge in G.edges])
    average_weight = total_weight / total_edges
    min_weight = min([G.edges[edge]["weight"] for edge in G.edges])
    max_weight = max([G.edges[edge]["weight"] for edge in G.edges])

    graph_state = {}
    for donation in all_donations:
        if donation.ngo_id is not None:
            state1 = donation.donor_id.pincode.city
            state2 = donation.ngo_id.pincode.city
            amount = donation.quantity
            if state1 not in graph_state:
                graph_state[state1] = {}
            if state2 not in graph_state:
                graph_state[state2] = {}
            graph_state[state1][state2] = amount
            graph_state[state2][state1] = amount

    G_state = nx.DiGraph()
    for state1 in graph_state:
        for state2 in graph_state[state1]:
            amount = graph_state[state1][state2]
            G_state.add_edge(state1, state2, weight=amount)

    total_edges_state = G_state.number_of_edges()
    total_weight_state = sum([G_state.edges[edge]["weight"] for edge in G_state.edges])
    average_weight_state = total_weight / total_edges
    min_weight_state = min([G_state.edges[edge]["weight"] for edge in G_state.edges])
    max_weight_state = max([G_state.edges[edge]["weight"] for edge in G_state.edges])

    return render(
        request,
        "inventory/donations_stats.html",
        {
            "image": image,
            "plot_data2": plot_data2,
            "plot_data3": plot_data3,
            "plot_data1": plot_data1,
            "plot_data5": plot_data5,
            **context,
        },
    )



@login_required
def ngo_stats(request):

    ngo_count = ngo.objects.count()
    donor_count = donor.objects.filter(is_superuser=False).count()
    total_donations = donations.objects.count()
    avg_quantity = donations.objects.aggregate(Avg("quantity"))
    max_quantity = donations.objects.aggregate(Max("quantity"))
    total_quantity = donations.objects.aggregate(Sum("quantity"))
    avg_quantity = int(avg_quantity["quantity__avg"])

    context = {
        "ngo_count": ngo_count,
        "donor_count": donor_count,
        "total_donations": total_donations,
        "avg_quantity": avg_quantity,
        "max_quantity": max_quantity,
        "total_quantity": total_quantity,
    }

    # --------------------------------------------------------------------------------------------------------------------
    """
    Calculating Donors Retention rate
    """
    retention_period = timedelta(days=365)
    start_date = (dt.now() - retention_period).replace(day=1)
    total_donors = donations.objects.count()
    end_date = dt.now().replace(day=1)

    # Create a list of all months within the retention period
    all_months = []
    while start_date <= end_date:
        all_months.append(start_date)
        start_date += relativedelta(months=1)

    returning_donors = {}
    for donation in donations.objects.filter(
        donation_date__gt=dt.now() - retention_period
    ):
        month = donation.donation_date.replace(day=1)
        donor_id = donation.donor_id.id
        donors = donor.objects.filter(id=donor_id).first()
        if donor_id in returning_donors.get(month - retention_period, set()):
            continue
        if (
            donors is not None
            and donations.objects.filter(
                donor_id=donor_id,
                donation_date__lt=month,
                donation_date__gt=month - retention_period,
            ).exists()
        ):
            returning_donors.setdefault(month, set()).add(donor_id)

    returning_donors = sorted(returning_donors.items())

    # Create a dictionary with all months as keys, and 0 as the initial value
    retention_dict = {}
    for month in all_months:
        retention_dict[month] = 0

    # Update the retention dictionary with the actual retention rates
    for month, returning in returning_donors:
        retention_dict[month] = len(returning) / total_donors * 100

    # Convert the retention dictionary into two lists (months and rates)
    months = [month.strftime("%b %Y") for month in retention_dict.keys()]
    rates = [rate for rate in retention_dict.values()]

    buf = io.BytesIO()
    fig, ax = plt.subplots()
    ax.bar(months, rates, color="orange")
    ax.set_ylabel("Returning donors (%)")
    ax.set_xlabel("Month")
    ax.set_title("Donor retention over time")
    plt.xticks(rotation=45, fontsize=7)

    # Convert the PNG image to a base64 string for display on the web page
    plt.savefig(buf, format="png")
    buf.seek(0)
    plot_data1 = base64.b64encode(buf.getvalue()).decode("ascii")

    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------
    """
    Donations per month Distribution: Overall, User's city and User-specific 
    """
    today = dt.now()
    first_day_of_month = today.replace(day=1)

    # Create a list of all the months in the current year
    all_months = []
    for i in range(12):
        month = (first_day_of_month - timedelta(days=30 * i)).strftime("%b %Y")
        all_months.append(month)
    city_donations = list(
        donations.objects.filter(pincode__code=request.user.pincode.code)
        .annotate(month=TruncMonth("donation_date"))
        .values("month")
        .annotate(total_donations=Sum("quantity"))
        .order_by("month")
    )
    tot_donations = list(
        donations.objects.annotate(month=TruncMonth("donation_date"))
        .values("month")
        .annotate(total_donations=Sum("quantity"))
        .order_by("month")
    )

    # Create a dictionary with all the months and their corresponding donation amounts
    city_donation_dict = {month: 0 for month in all_months}
    tot_donation_dict = {month: 0 for month in all_months}

    # Populate the dictionaries with the actual donation amounts
    for donation in city_donations:
        month_str = donation["month"].strftime("%b %Y")
        city_donation_dict[month_str] = donation["total_donations"]
    for donation in tot_donations:
        month_str = donation["month"].strftime("%b %Y")
        tot_donation_dict[month_str] = donation["total_donations"]

    # Convert the dictionaries to lists for plotting
    city_month = list(city_donation_dict.keys())
    city_donation_amounts = list(city_donation_dict.values())
    tot_month = list(tot_donation_dict.keys())
    tot_donation_amounts = list(tot_donation_dict.values())

    # Plot the donations per month
    fig, ax = plt.subplots()
    ax.plot(city_month, city_donation_amounts, label="City Donations", color="black")
    ax.plot(tot_month, tot_donation_amounts, label="Total Donations", color="yellow")
    ax.set_xlabel("Month")
    ax.set_ylabel("Donation Amount")
    ax.set_title("Donations per Month")
    ax.legend()
    plt.xticks(rotation=45, fontsize=7)

    # Save the plot to a PNG image
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)

    # Convert the PNG image to a base64 string for display on the web page
    plot_data2 = base64.b64encode(buf.getvalue()).decode("ascii")

    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------

    return render(
        request,
        "inventory/ngo_stats.html",
        {"plot_data2": plot_data2, "plot_data1": plot_data1, **context},
    )
