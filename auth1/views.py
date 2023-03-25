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
            login(self.request, self.object, backend="django.contrib.auth.backends.ModelBackend")
            return response
