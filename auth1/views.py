from auth1.constants import *
from auth1.forms import *
from django.contrib.auth import logout, login
from django.urls import reverse_lazy
from django.shortcuts import redirect, render
from django.views import generic
from auth1.backends import MyUserBackend
from django.db.models import Sum


def home_view(request):
    return render(request, HOME)


def donor_home(request):
    user_donation = Donations.objects.filter(donor_id=request.user)
    lives = user_donation.filter(ngo_status=False, donor_status=False).aggregate(
        Sum(QUANTITY)
    )
    count = user_donation.count()
    context = {
        "count": count,
        "lives": lives,
    }
    return render(request, DONOR_HOME_URL, context)


def ngo_home(request):
    return render(request, NGO_HOME_URL)


def logout_view(request):
    logout(request)
    return redirect(HOME_URL)


def ngo_login_view(request):
    """
    This view handles the login functionality for NGOs.

    :param request:
        The HTTP request object.

    :return:
        - If the request method is POST and the user is authenticated then it
          redirectes to the NGO's homepage.
        - If the request method is POST and the user is invalid an error message
          is rendered
        - If the request method is GET, the login page is rendered.
    """
    if request.method == "POST":
        username = request.POST[USERNAME]
        password = request.POST[PASSWORD]
        user = MyUserBackend.authenticate(
            request,
            username=username,
            password=password,
            backend=MY_BACKEND,
        )

        if (user is not None) and (user.is_ngo):
            login(request, user, backend=MY_BACKEND)
            return redirect(NGO_HOME)
        else:
            return render(request, LOGIN_PAGE, {ERROR: ERROR_MSG})
    else:
        return render(request, LOGIN_PAGE)


def donor_login_view(request):
    """
    This view handles the login functionality for Donors.

    :param request:
        The HTTP request object.

    :return:
        - If the request method is POST and the user is authenticated then it
          redirectes to the NGO's homepage.
        - If the request method is POST and the user is invalid an error message
          is rendered
        - If the request method is GET, the login page is rendered.
    """
    if request.method == "POST":
        username = request.POST[USERNAME]
        password = request.POST[PASSWORD]
        user = MyUserBackend.authenticate(
            request,
            username=username,
            password=password,
            backend=MY_BACKEND,
        )
        if (user is not None) and (not user.is_ngo):
            login(request, user, backend=DJANG_BACKEND)
            return redirect(DONOR_HOME)
        else:
            return render(request, LOGIN_PAGE, {ERROR: ERROR_MSG})
    else:
        return render(request, LOGIN_PAGE)


class NgoSignUpView(generic.CreateView):
    """
    This view is used to display the NGO sign-up form and handle form
    submissions.
    """

    form_class = ngoUserCreationForm
    template_name = SIGNUP_PAGE
    success_url = reverse_lazy(NGO_HOME)

    def form_valid(self, form):
        if form.is_valid():
            donation = form.save(commit=False)
            donation.latitude = form.cleaned_data[LATITUDE]
            donation.longitude = form.cleaned_data[LONGITUDE]
            donation.save()
            response = super().form_valid(form)
            login(self.request, self.object, backend=MY_BACKEND)
            return response


class DonorSignUpView(generic.CreateView):
    """
    This view is used to display the Donor sign-up form and handle form
    submissions.
    """

    form_class = donorUserCreationForm
    template_name = SIGNUP_PAGE
    success_url = reverse_lazy(DONOR_HOME)

    def form_valid(self, form):
        """
        Validates the donation form and saves the donation object to the
        database.

        :param form:
            the donation form that is to be validated

        :return:
            HTTP response object called from parent class
        """
        if form.is_valid():
            donation = form.save(commit=False)
            donation.latitude = form.cleaned_data[LATITUDE]
            donation.longitude = form.cleaned_data[LONGITUDE]
            donation.save()
            response = super().form_valid(form)
            user = form.save()
            user.save()
            login(
                self.request,
                self.object,
                backend=DJANG_BACKEND,
            )
            return response
