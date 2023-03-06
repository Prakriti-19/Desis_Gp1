from . import views
from django.urls import path
from inventory.views import *
from auth1.views import *


urlpatterns = [
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("donate/", donate, name="add_donation"),
    path("list/",donations_list, name="donations_list"),
    path("ngo_register/", views.NgoSignUpView.as_view(), name="ngo_register"),
    path("donor_register/", views.DonorSignUpView.as_view(), name="donor_register"),
    path("", views.HomeView2.as_view(), name="home"),
    path("rp", redeem_points, name="redeem_points"),
    path("dp", donate_points, name="donate_points"),
    path("rs", redeem_success, name="redeem_success"),
    path("ngo_login/", views.NgoLoginView, name="ngo_login"),
    path("donor_login/", views.DonorLoginView, name="donor_login"),
]