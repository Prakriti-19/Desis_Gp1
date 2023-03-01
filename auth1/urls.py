from . import views
from django.urls import path
from inventory.views import *
from auth1.views import *


urlpatterns = [
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("donate/", DonationView.as_view(), name="add_donation"),
    path("list/",donations_list, name="donations_list"),
    path("nr/", views.NgoSignUpView.as_view(), name="ngo_register"),
    path("dr/", views.DonorSignUpView.as_view(), name="donor_register"),
    path("", views.HomeView.as_view(), name="home"),
    path("nl/", views.NgoLoginView, name="ngo_login"),
    path("dl/", views.DonorLoginView, name="donor_login"),
]