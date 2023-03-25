from auth1.forms import *
from django.contrib.auth import logout, login
from django.urls import reverse_lazy
from django.shortcuts import redirect, render
from django.views import generic
from auth1.backends import MyUserBackend
from django.db.models import Sum


def home_view(request):
    context = {
        "title": "HandsForHunger | Home",
    }
    return render(request, "home.html", context)


def donor_home(request):
    user_donation = donations.objects.filter(donor_id=request.user)
    lives = user_donation.filter(ngo_status=False, donor_status=False).aggregate(
        Sum("quantity")
    )
    count = user_donation.count()
    context = {
        "count": count,
        "lives": lives,
    }
    return render(request, "d_h.html", context)


def ngo_home(request):
    return render(request, "n_h.html")


def logout_view(request):
    logout(request)
    return redirect("/")


def ngo_login_view(request):
    """
    This view handles the login functionality for NGOs.

    Returns:
        If the login is successful, redirects the user to the NGO home page. 
        If the login fails, displays an error message.

    Variables:
        - username: the username entered by the user.
        - password: the password entered by the user.
        - user: the user object returned by the authentication backend.
    """
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = MyUserBackend.authenticate(
            request,
            username=username,
            password=password,
            backend="auth1.backends.MyUserBackend",
        )

        if user is not None and user.is_ngo:
            login(request, user, backend="auth1.backends.MyUserBackend")
            return redirect("ngo_home")
        else:
            return render(
                request, "login.html", {"error_message": "Invalid login credentials"}
            )
    else:
        return render(request, "login.html")


def donor_login_view(request):
    """
    This view handles the login functionality for Donors.

    Returns:
        If the login is successful, redirects the user to the NGO home page.
        If the login fails, displays an error message.

    Variables:
        - username: the username entered by the user.
        - password: the password entered by the user.
        - user: the user object returned by the authentication backend.
    """
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = MyUserBackend.authenticate(
            request,
            username=username,
            password=password,
            backend="auth1.backends.MyUserBackend",
        )
        if user is not None and not user.is_ngo:
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            return redirect("donor_home")
        else:
            return render(
                request, "login.html", {"error_message": "Invalid login credentials"}
            )
    else:
        return render(request, "login.html")


class NgoSignUpView(generic.CreateView):
    """
    This view is used to display the NGO sign-up form and handle form submissions.

    Attributes:
        - form_class: The form used for the sign-up process.
        - template_name: The name of the HTML template used for rendering the sign-up form.
        - success_url: The URL to redirect to after a successful sign-up.

    Methods:
        - form_valid: Called when a valid form is submitted. Saves the form data, logs the user in and redirects to success_url.
    """

    form_class = ngoUserCreationForm
    template_name = "signup.html"
    success_url = reverse_lazy("ngo_home")

    def form_valid(self, form):
        if form.is_valid():
            donation = form.save(commit=False)
            donation.latitude = form.cleaned_data["latitude"]
            donation.longitude = form.cleaned_data["longitude"]
            donation.save()
            response = super().form_valid(form)
            login(self.request, self.object, backend="auth1.backends.MyUserBackend")
            return response


class DonorSignUpView(generic.CreateView):
    """
    This view is used to display the Donor sign-up form and handle form submissions.

    Attributes:
        - form_class: The form used for the sign-up process.
        - template_name: The name of the HTML template used for rendering the sign-up form.
        - success_url: The URL to redirect to after a successful sign-up.

    Methods:
        - form_valid: Called when a valid form is submitted. Saves the form data, logs the user in and redirects to success_url.
    """

    form_class = donorUserCreationForm
    template_name = "signup.html"
    success_url = reverse_lazy("donor_home")

    def form_valid(self, form):
        if form.is_valid():
            donation = form.save(commit=False)
            donation.latitude = form.cleaned_data["latitude"]
            donation.longitude = form.cleaned_data["longitude"]
            donation.save()
            response = super().form_valid(form)
            user = form.save()
            user.save()
            response = super().form_valid(form)
            login(
                self.request,
                self.object,
                backend="django.contrib.auth.backends.ModelBackend",
            )
            return response
