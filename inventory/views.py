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

from payment.constants import *

matplotlib.use("Agg")


@login_required
# decorator used to ensure only after logging in one can access this function
def donate(request):
    """
    View function that handles the donation form submission and rendering the
    donation form page.

    :param request:
        HTTP request object(POST)

    :return:
        HTTP response which renders HTML page
    """
    if request.method == "POST":
        form = DonationForm(request.POST, user=request.user)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.latitude = form.cleaned_data[LATITUDE]
            donation.longitude = form.cleaned_data[LONGITUDE]
            donation.save()
            return redirect(DONOR_HOME)
    else:
        form = DonationForm(user=request.user)
    return render(request, "inventory/donate.html", {FORM: form})


@login_required
def redeem_points(request):
    """
    View function that handles DESCOINS redemption

    :param request:
        HTTP request object(POST)

    :return:
        HTTP response which renders HTML page
    """
    if request.method == "POST":
        descoins_to_redeem = int(request.POST.get(DESCOINS))
        donor = request.user
        if donor.descoins >= descoins_to_redeem:
            # TODO: Solve read write inconsistency problem that might arise
            donor.descoins -= descoins_to_redeem
            donor.save()
            Transaction.objects.create(
                sender=donor.id,
                receiver=None,
                descoins_transferred=descoins_to_redeem,
                type=D2U,
                timestamp=timezone.now(),
            )
            messages.success(request, SUCCESS_REDEEM)
        else:
            messages.error(request, FAIL_REDEEM)
    return render(request, "inventory/redeem_points.html")


@login_required
def mail(request, email):
    """
    View function to render a donation email template with the provided donor
    email address.
    """
    context = {
        DONOR_MAIL: email,
    }
    return render(request, "inventory/donation_email.html", context)


@login_required
def donate_points(request, ngo_id):
    """
    View function to handle donation of DESCOINS to an NGO.
    """
    if request.method == "POST":
        descoins_to_donate = request.POST.get(DESCOINS)
        if (descoins_to_donate is not None) and (descoins_to_donate.strip() != ""):
            descoins_to_donate = int(descoins_to_donate)
            donor = request.user
            ng = ngo.objects.get(id=ngo_id)
            if donor.descoins >= descoins_to_donate:
                # TODO: Solve read write inconsistency problem that might arise
                donor.descoins -= descoins_to_donate
                donor.save()
                ng.descoins += descoins_to_donate
                ng.save()
                Transaction.objects.create(
                    sender=donor.id,
                    receiver=ngo_id,
                    descoins_transferred=descoins_to_donate,
                    type=D2N,
                    timestamp=timezone.now(),
                )
                messages.success(request, SUCCESS_REDEEM)
            else:
                messages.warning(request, FAIL_REDEEM)
        else:
            messages.warning(request, NULL_FEILD_ERROR)
    ng = ngo.objects.get(id=ngo_id)
    context = {"ngo": ng}
    return render(request, "inventory/donatep.html", context)


@login_required
def process_payment(request):
    """
    View function that processes a payment request.
    """
    if request.method == "POST":
        amount = request.POST.get(AMOUNT)
        if (amount is None) or (not amount.isdigit()):
            return HttpResponseBadRequest(INVALID)
        context = {AMOUNT: amount}
        return render(request, "payment_success.html", context)
    else:
        return HttpResponseBadRequest(INVALID)


@login_required
def donations_list(request):
    """
    Handles request to filter donations as per queries

    :return:
        A rendered HTML page that displays the list of donations.
    """
    codes = request.GET.get(PIN)

    min_quantity = request.GET.get(MIN)
    if (min_quantity is None) or (min_quantity == ""):
        min_quantity = DEFAULT_MIN

    max_quantity = request.GET.get(MAX)
    if (max_quantity is None) or (max_quantity == ""):
        max_quantity = DEFAULT_MAX

    now = timezone.now()
    filter_distance = request.GET.get(DISTANCE)
    if (filter_distance is None) or (filter_distance == ""):
        filter_distance = DEFAULT_MAX

    if (codes is None) or (codes == ""):
        donation = donations.objects.filter(
            Q(exp_date__gt=now)
            & Q(quantity__range=(min_quantity, max_quantity))
            & (Q(ngo_status=True) | Q(donor_status=True))
        ).order_by(EXP_DATE)

    else:
        donation = donations.objects.filter(
            Q(exp_date__gt=now)
            & Q(pincode__code=codes)
            & Q(quantity__range=(min_quantity, max_quantity))
            & (Q(ngo_status=True) | Q(donor_status=True))
        ).order_by(EXP_DATE)

    # List to store donations along with distances
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
    Displays list of all NGOs in the system, along with their distance from the
    current user's location.

    :return:
        rendered HTML page containing a list of the NGOs
    """
    ngos = ngo.objects.all()
    user_latitude = request.user.latitude
    user_longitude = request.user.longitude
    for ng in ngos:
        ngo_latitude = ng.latitude
        ngo_longitude = ng.longitude
        distance = haversine(user_latitude, user_longitude, ngo_latitude, ngo_longitude)
        ng.distance = round(distance, 2)

    context = {NGOS: ngos}
    return render(request, "inventory/ngo_list.html", context)


def haversine(lat1, lon1, lat2, lon2):
    """
    This function calculates the haversine distance between two geographical
    points on Earth.

    :param lat1:
        latitude of the first point
    :param lat12:
        latitude of the second point
    :param lon1:
        latitude of the first point
    :param lon2:
        longitude of the second point

    :return:
        float type value: the distance between two points in km
    """
    R = 6371  # radius of Earth in kilometers
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = (
        sin(dlat / CONST_2) ** CONST_2
        + cos(lat1) * cos(lat2) * sin(dlon / CONST_2) ** CONST_2
    )
    c = CONST_2 * atan2(sqrt(a), sqrt(CONST_1 - a))
    distance = R * c
    return distance


@login_required
def update_donation_status_donor(request):
    """
    Updates the donor_status of a donation, confirming that the donation was
    given by the ngo

    :returns:
        HTTP response
    """
    if request.method == "POST":
        donation_i = request.POST.get(ID1)
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
    Updates the ngo_status of a donation, confirming that the donation is taken
    by the ngo

    :returns:
        HTTP response
    """
    if request.method == "POST":
        donation_id = request.POST.get(ID2)
        try:
            donation = donations.objects.get(id=donation_id)
            donation.ngo_id = request.user
            donation.ngo_status = False
            donation.save()
            if donation.donor_status == False and donation.ngo_status == False:
                update_points(donation.donor_id.id, donation.quantity, request.user.id)
        except donations.DoesNotExist:
            return HttpResponse(DONATION_ERROR)
        else:
            return redirect("donations_list")


def update_points(donor_id, quantity, ngo_id):
    """
    This function updates the descoins of the donor and ngo after a donation is
    made

    :param donor_id:
        ID of the donor
    :param quantity:
        Quantity of donation
    :paramngo_id:
        ID of the ngo

    :returns:
        None
    """
    ngos = ngo.objects.get(id=ngo_id)
    donors = donor.objects.get(id=donor_id)
    donors.descoins += BASE_VAL * quantity
    ngos.descoins -= BASE_VAL * quantity
    donors.save()
    ngos.save()
    Transaction.objects.create(
        sender=ngos.id,
        receiver=donors.id,
        descoins_transferred=BASE_VAL * quantity,
        type=N2D,
        timestamp=timezone.now(),
    )


@login_required
def donor_history(request):
    """
    This view displays the history of donations made by the currently logged-in
    donor.

    :return:
        HTML page that lists all the donations made by the donor
    """
    donor_instance = donor.objects.get(id=request.user.id)
    donations_made = donor_instance.donations_made().order_by("donation_date")

    context = {
        DONOR: donor_instance,
        DONATIONS_MADE: donations_made,
    }
    return render(request, "inventory/donor_history.html", context)


@login_required
def donations_stats(request):
    """
    This function handles all the statistical analysis done on the data
    """

    # Retrieve all donations and donors
    all_donations = donations.objects.all()
    all_donors = donor.objects.all()
    user_donation = all_donations.filter(donor_id=request.user.id)

    ngo_count = ngo.objects.count()
    donor_count = donor.objects.filter(is_superuser=False).count()
    total_donations = all_donations.count()
    avg_quantity = all_donations.aggregate(Avg(QUANTITY))
    max_quantity = all_donations.aggregate(Max(QUANTITY))
    total_quantity = all_donations.aggregate(Sum(QUANTITY))
    avg_quantity = int(avg_quantity[QUANT_AVG])

    # -----------------------------------------------------------------------------------------------------------------------------
    """
    Calculating Donors Retention rate
    """
    retention_period = timedelta(days=YEAR_DAYS)
    start_date = (dt.now() - retention_period).replace(day=CONST_1)
    end_date = dt.now().replace(day=CONST_1)
    all_months = []

    # Create a list of all the months in the retention period
    while start_date <= end_date:
        all_months.append(start_date)
        start_date += relativedelta(months=1)

    # Dictionary of returning donors for each month in the retention period
    returning_donors = {}

    # Loop through all the donations made in the retention period
    for donation in all_donations.filter(donation_date__gt=dt.now() - retention_period):
        month = donation.donation_date.replace(day=CONST_1)
        donor_id = donation.donor_id.id
        donors = all_donors.filter(id=donor_id).first()

        # Using a set to store ids for all donors that have returned this month
        # and checking if the cutrrent user is already present in the set or not
        if donor_id in returning_donors.get(month - retention_period, set()):
            continue

        # Checking if the donor has made a donation in the previous retention period
        if (donors is not None) and (
            all_donations.filter(
                donor_id=donor_id,
                donation_date__lt=month,
                donation_date__gt=month - retention_period,
            ).exists()
        ):
            # Mark the donor as a returning donor for this m onth
            returning_donors.setdefault(month, set()).add(donor_id)

    # Sort the returning donors by month
    returning_donors = sorted(returning_donors.items())

    # Create a dictionary to store the retention rates for each month
    retention_dict = {}
    for month in all_months:
        retention_dict[month] = CONST_0

    # Update the retention dictionary with the actual retention rates
    for month, returning in returning_donors:
        # Calculate the retention rate as the number of returning donors divided by the total number of donors
        retention_rate = len(returning) / len(all_donors) * PERCENT

        # Add the retention rate to the retention dictionary for this month
        retention_dict[month] = retention_rate

    # Convert the retention dictionary into two lists (months and rates)
    months = [month.strftime("%b %Y") for month in retention_dict.keys()]
    rates = [rate for rate in retention_dict.values()]

    buf = io.BytesIO()
    fig, ax = plt.subplots()
    ax.bar(months, rates, color=COLOR_1)
    ax.set_ylabel(PLOT1_Y)
    ax.set_xlabel(MONTH)
    ax.set_title(PLOT1_LABEL)
    plt.xticks(rotation=ROTATION, fontsize=FONT_SIZE)

    # Convert the PNG image to a base64 string for display on the web page
    plt.savefig(buf, format=FORMAT)
    buf.seek(CONST_0)
    plot_data1 = base64.b64encode(buf.getvalue()).decode(ASCII)

    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------
    """
    Donations per month Distribution: Overall, User's city and User-specific 
    """
    today = dt.now()
    first_day_of_month = today.replace(day=CONST_1)

    # Create a list of all the months in the current year
    all_months = []
    for i in range(YEAR_LEN):
        month = (first_day_of_month - timedelta(days=MONTH_DAYS * i)).strftime("%b %Y")
        all_months.append(month)
    all_months.reverse()
    # Query the database for the user's donations per month
    user_donations = list(
        user_donation.annotate(month=TruncMonth(DONATION_DATE))
        .values(MONTH)
        .annotate(total_donations=Sum(QUANTITY))
        .order_by(MONTH)
    )
    # Query the database for the city's donations per month
    city_donations = list(
        all_donations.filter(pincode__code=request.user.pincode.code)
        .annotate(month=TruncMonth(DONATION_DATE))
        .values(MONTH)
        .annotate(total_donations=Sum(QUANTITY))
        .order_by(MONTH)
    )
    tot_donations = list(
        all_donations.annotate(month=TruncMonth(DONATION_DATE))
        .values(MONTH)
        .annotate(total_donations=Sum(QUANTITY))
        .order_by(MONTH)
    )

    # Create a dictionary with all the months and their corresponding donation amounts
    user_donation_dict = {month: 0 for month in all_months}
    city_donation_dict = {month: 0 for month in all_months}
    tot_donation_dict = {month: 0 for month in all_months}

    # Populate the dictionaries with the actual donation amounts
    for donation in user_donations:
        month_str = donation[MONTH].strftime("%b %Y")
        user_donation_dict[month_str] = donation[TOTAL_DONATION]
    for donation in city_donations:
        month_str = donation[MONTH].strftime("%b %Y")
        city_donation_dict[month_str] = donation[TOTAL_DONATION]
    for donation in tot_donations:
        month_str = donation[MONTH].strftime("%b %Y")
        tot_donation_dict[month_str] = donation[TOTAL_DONATION]

    # Convert the dictionaries to lists for plotting
    user_month = list(user_donation_dict.keys())
    user_donation_amounts = list(user_donation_dict.values())
    city_month = list(city_donation_dict.keys())
    city_donation_amounts = list(city_donation_dict.values())
    tot_month = list(tot_donation_dict.keys())
    tot_donation_amounts = list(tot_donation_dict.values())

    # Plot the donations per month
    fig, ax = plt.subplots()
    ax.plot(user_month, user_donation_amounts, label=MY_LABEL, color=COLOR_1)
    ax.plot(city_month, city_donation_amounts, label=CITY_LABEL, color=COLOR_3)
    ax.plot(tot_month, tot_donation_amounts, label=OVERALL, color=COLOR_2)
    ax.set_xlabel(MONTH)
    ax.set_ylabel(PLOT2_Y)
    ax.set_title(PLOT2_LABEL)
    ax.legend()
    plt.xticks(rotation=ROTATION, fontsize=FONT_SIZE)

    # Save the plot to a PNG image
    buf = io.BytesIO()
    plt.savefig(buf, format=FORMAT)
    buf.seek(CONST_0)

    # Convert the PNG image to a base64 string for display on the web page
    plot_data2 = base64.b64encode(buf.getvalue()).decode(ASCII)

    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------
    """
    Calculating Donation ratio of user in his city
    """
    # Calculates sum of the quantity field for donations and returns a dictionary with a key quantity__sum
    total_donations_ = all_donations.aggregate(Sum(QUANTITY))[QUANT_SUM]
    user_donations = user_donation.aggregate(Sum(QUANTITY))[QUANT_SUM]
    if total_donations_ is None:
        total_donations_ = CONST_0
    if user_donations is None:
        user_donations = CONST_0
    percentage = round(user_donations / total_donations_* PERCENT, CONST_2)

    # Define the labels, sizes, colors and explosion for the pie chart
    labels = [MY_LABEL, OTHERS_LABEL]
    sizes = [percentage, PERCENT - percentage]
    colors = [COLOR_1, COLOR_2]
    explode = (EXPLOD_PERCENT, CONST_0)

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
    plt.axis(IMAGE_AXIS)
    plt.title(IMAGE_LABEL)
    plt.legend(title=LEGEND)

    # Convert the PNG image to a base64 string for display on the web page
    buffer = io.BytesIO()
    plt.savefig(buffer, format=FORMAT)
    buffer.seek(CONST_0)
    image = base64.b64encode(buffer.getvalue()).decode(IMAGE_CODE)

    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------
    """
    Donation Type Distribution: Overall and User-specific
    """
    # Get the user's donation counts
    user_homefood_count = (
        user_donation.filter(type=HOME_FOOD).aggregate(Sum(QUANTITY))[QUANT_SUM]
        or CONST_0
    )
    user_party_count = (
        user_donation.filter(type=PARTY).aggregate(Sum(QUANTITY))[QUANT_SUM] or CONST_0
    )
    user_restro_count = (
        user_donation.filter(type=RESTAURANT).aggregate(Sum(QUANTITY))[QUANT_SUM]
        or CONST_0
    )
    user_other_count = (
        user_donation.filter(type=OTHER).aggregate(Sum(QUANTITY))[QUANT_SUM] or CONST_0
    )

    # Get the overall donation counts
    overall_homefood_count = (
        all_donations.filter(type=HOME_FOOD).aggregate(Sum(QUANTITY))[QUANT_SUM]
        or CONST_0
    )
    overall_party_count = (
        all_donations.filter(type=PARTY).aggregate(Sum(QUANTITY))[QUANT_SUM] or CONST_0
    )
    overall_restro_count = (
        all_donations.filter(type=RESTAURANT).aggregate(Sum(QUANTITY))[QUANT_SUM]
        or CONST_0
    )
    overall_other_count = (
        all_donations.filter(type=OTHER).aggregate(Sum(QUANTITY))[QUANT_SUM] or CONST_0
    )

    # x-coordinates for user bars
    user_x = [i - XAXIS_SPACE for i in range(len(types))]
    # x-coordinates for overall bars
    overall_x = [i + XAXIS_SPACE for i in range(len(types))]
    bar_width = BAR_WIDTH
    fig, ax = plt.subplots()
    ax.bar(
        user_x,
        [user_homefood_count, user_party_count, user_restro_count, user_other_count],
        label=MY_LABEL,
        color=COLOR_2,
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
        label=OVERALL,
        color=COLOR_1,
        width=bar_width,
    )

    ax.set_title(PLOT3_LABEL)
    ax.set_xlabel(PLOT3_X)
    ax.set_ylabel(QUANTITY)
    ax.set_xticks(range(len(types)))
    ax.set_xticklabels(types)
    ax.legend()

    # Save the figure to a buffer in PNG format
    buf = io.BytesIO()
    plt.savefig(buf, format=FORMAT)
    buf.seek(CONST_0)

    # Convert the PNG image to a base64 string for display on the web page
    plot_data3 = base64.b64encode(buf.getvalue()).decode(ASCII)

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
        week_num = date.isocalendar()[1] - CONST_1
        day_num = date.weekday()
        donation_array[week_num][day_num] = donation_dict[date.strftime("%Y-%m-%d")]

    donation_array = np.transpose(donation_array)
    x_labels = []
    l = 0
    for i in range(0, 52):
        if i % 4 == 0:
            x_labels.append(k[l])
            l += 1
        else:
            x_labels.append("")
    fig, ax = plt.subplots(figsize=(SMALL_MAX_LENGTH, 3))
    heatmap = ax.imshow(donation_array, cmap="Oranges")
    for i in range(len(donation_array)):
        for j in range(len(donation_array[i])):
            rect = plt.Rectangle(
                (j - CONST_1 / CONST_2, i - CONST_1 / CONST_2),
                CONST_1,
                CONST_1,
                linewidth=1,
                edgecolor=COLOR_4,
                facecolor="none",
            )
            ax.add_patch(rect)
    cbar = ax.figure.colorbar(heatmap, ax=ax)
    ax.set_xticks(np.arange(len(x_labels)))
    ax.set_xticklabels(x_labels)
    plt.setp(
        ax.get_xticklabels(), rotation=ROTATION, ha="right", rotation_mode="anchor" )
    ax.set_yticks(np.arange(len(y_labels)))
    ax.set_yticklabels(y_labels)
    ax.set_title(PLOT5_LABEL)
    fig.tight_layout()
    buf5 = io.BytesIO()
    plt.savefig(buf5, format=FORMAT)
    buf5.seek(CONST_0)

    # Convert the PNG image to a base64 string for display on the web page
    plot_data5 = base64.b64encode(buf5.getvalue()).decode(ASCII)

    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------
    start_date = datetime.date.today() - timedelta(days=YEAR_DAYS)
    end_date = datetime.date.today()

    # Retrieve all transactions involving the user as either sender or receiver
    user_transactions = Transaction.objects.filter(
        Q(sender=request.user.id) | Q(receiver=request.user.id)
    )

    # Create a dictionary of transaction amounts keyed by date
    daily_totals = {}
    for transaction in user_transactions:
        transaction_date = transaction.timestamp.date()
        transaction_amount = transaction.descoins_transferred
        if transaction_date >= start_date and transaction_date <= end_date:
            if transaction_date in daily_totals:
                daily_totals[transaction_date] += transaction_amount
            else:
                daily_totals[transaction_date] = transaction_amount
    dates = sorted(daily_totals.keys())
    amounts = [daily_totals[date] for date in dates]

    # Create a figure and axis object
    fig, ax = plt.subplots()
    ax.plot(dates, amounts,color = COLOR_2)
    ax.set_xlabel('Date')
    ax.set_ylabel('Transaction Amount')
    ax.set_title('Daily Transaction Amounts')

    # Set x-axis tick labels
    date_labels = [date.strftime('%Y-%m-%d') for date in dates]  
    ax.set_xticklabels(date_labels, rotation=90, fontsize=4, ha='right')
    ax.set_xticks(dates)  # set the number of ticks to match the number of dates

    # Set y-axis tick labels
    amount_labels = ['{:.2f}'.format(amount) for amount in ax.get_yticks()]
    ax.set_yticklabels(amount_labels)


    # Save the plot to a buffer and encode it as base64 for display in the HTML template
    buffer9 = io.BytesIO()
    plt.savefig(buffer9, format=FORMAT)
    buffer9.seek(CONST_0)
    plot_data6 = base64.b64encode(buffer9.getvalue()).decode(ASCII)

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
    total_weight = sum([G.edges[edge][WEIGHT] for edge in G.edges])
    average_weight = total_weight / total_edges
    max_weight = max([G.edges[edge][WEIGHT] for edge in G.edges])

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
    total_weight_state = sum([G_state.edges[edge][WEIGHT] for edge in G_state.edges])
    average_weight_state = total_weight / total_edges
    max_weight_state = max([G_state.edges[edge][WEIGHT] for edge in G_state.edges])

    # Create context dictionary to pass variables to the HTML template
    context = {
        "ngo_count": ngo_count,
        "donor_count": donor_count,
        "total_donations": total_donations,
        "avg_quantity": avg_quantity,
        "max_quantity": max_quantity,
        "total_quantity": total_quantity,
        "total_edges": total_edges,
        "average_weight": average_weight,
        "total_edges_state": total_edges_state,
        "average_weight_state": average_weight_state,
    }
    return render(
        request,
        "inventory/donations_stats.html",
        {
            "image": image,
            "plot_data2": plot_data2,
            "plot_data6": plot_data6,
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
    avg_quantity = donations.objects.aggregate(Avg(QUANTITY))
    max_quantity = donations.objects.aggregate(Max(QUANTITY))
    total_quantity = donations.objects.aggregate(Sum(QUANTITY))
    avg_quantity = int(avg_quantity[QUANT_AVG])

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
    start_date = (dt.now() - retention_period).replace(day=CONST_1)
    total_donors = donations.objects.count()
    end_date = dt.now().replace(day=CONST_1)

    # Create a list of all months within the retention period
    all_months = []
    while start_date <= end_date:
        all_months.append(start_date)
        start_date += relativedelta(months=CONST_1)

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
        retention_dict[month] = CONST_0

    # Update the retention dictionary with the actual retention rates
    for month, returning in returning_donors:
        retention_dict[month] = len(returning) / total_donors * 100

    # Convert the retention dictionary into two lists (months and rates)
    months = [month.strftime("%b %Y") for month in retention_dict.keys()]
    rates = [rate for rate in retention_dict.values()]

    buf = io.BytesIO()
    fig, ax = plt.subplots()
    ax.bar(months, rates, color=COLOR_1)
    ax.set_ylabel(PLOT1_Y)
    ax.set_xlabel(MONTH)
    ax.set_title(PLOT1_LABEL)
    plt.xticks(rotation=ROTATION, fontsize=FONT_SIZE)

    # Convert the PNG image to a base64 string for display on the web page
    plt.savefig(buf, format=FORMAT)
    buf.seek(0)
    plot_data1 = base64.b64encode(buf.getvalue()).decode(ASCII)

    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------
    """
    Donations per month Distribution: Overall, User's city and User-specific 
    """
    today = dt.now()
    first_day_of_month = today.replace(day=CONST_1)
    all_donations = donations.all()

    # Create a list of all the months in the current year
    all_months = []
    for i in range(YEAR_LEN):
        month = (first_day_of_month - timedelta(days=MONTH_DAYS * i)).strftime("%b %Y")
        all_months.append(month)

    # Query the database for the city's donations per month
    city_donations = list(
        all_donations.filter(pincode__code=request.user.pincode.code)
        .annotate(month=TruncMonth(DONATION_DATE))
        .values(MONTH)
        .annotate(total_donations=Sum(QUANTITY))
        .order_by(MONTH)
    )
    tot_donations = list(
        all_donations.annotate(month=TruncMonth(DONATION_DATE))
        .values(MONTH)
        .annotate(total_donations=Sum(QUANTITY))
        .order_by(MONTH)
    )

    # Create a dictionary with all the months and their corresponding donation amounts
    user_donation_dict = {month: 0 for month in all_months}
    city_donation_dict = {month: 0 for month in all_months}
    tot_donation_dict = {month: 0 for month in all_months}

    # Populate the dictionaries with the actual donation amounts
    for donation in city_donations:
        month_str = donation[MONTH].strftime("%b %Y")
        city_donation_dict[month_str] = donation[TOTAL_DONATION]
    for donation in tot_donations:
        month_str = donation[MONTH].strftime("%b %Y")
        tot_donation_dict[month_str] = donation[TOTAL_DONATION]

    # Convert the dictionaries to lists for plotting
    city_month = list(city_donation_dict.keys())
    city_donation_amounts = list(city_donation_dict.values())
    tot_month = list(tot_donation_dict.keys())
    tot_donation_amounts = list(tot_donation_dict.values())

    # Plot the donations per month
    fig, ax = plt.subplots()
    ax.plot(city_month, city_donation_amounts, label=CITY_LABEL, color=COLOR_3)
    ax.plot(tot_month, tot_donation_amounts, label=OVERALL, color=COLOR_2)
    ax.set_xlabel(MONTH)
    ax.set_ylabel(PLOT2_Y)
    ax.set_title(PLOT2_LABEL)
    ax.legend()
    plt.xticks(rotation=ROTATION, fontsize=FONT_SIZE)

    # Save the plot to a PNG image
    buf = io.BytesIO()
    plt.savefig(buf, format=FORMAT)
    buf.seek(CONST_0)

    # Convert the PNG image to a base64 string for display on the web page
    plot_data2 = base64.b64encode(buf.getvalue()).decode(ASCII)

    return render(
        request,
        "inventory/ngo_stats.html",
        {"plot_data2": plot_data2, "plot_data1": plot_data1, **context},
    )
