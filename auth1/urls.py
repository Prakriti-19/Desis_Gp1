from . import views
from django.urls import path
from inventory.views import *
from auth1.views import *


urlpatterns = [
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("donate/", donate, name="add_donation"),
    path("stats/", donations_stats, name="stats"),
    path("list/",donations_list, name="donations_list"),
    path("donor_history/", donor_history, name="donor_history"),
    path("redeem_points/", redeem_points, name="redeem_points"),
    path("donate_points/", donate_points, name="donate_points"),
    path("redeem_success/", redeem_success, name="redeem_success"),
    path('donations/<int:pk>/', donation_details, name='donation-details'),
    path("update_donation_status/", update_donation_status, name="update_donation_status"),
    path("update_donation_status_ngo/", update_donation_status_ngo, name="update_donation_status_ngo"),
    path("ngo_login/", views.NgoLoginView, name="ngo_login"),
    path("ngo_register/", views.NgoSignUpView.as_view(), name="ngo_register"),
    path("donor_register/", views.DonorSignUpView.as_view(), name="donor_register"),
     path("ngo_home/", views.n_h.as_view(), name="n_home"),
    path("donor_home/", views.d_h.as_view(), name="d_home"),
    path("donor_login/", views.DonorLoginView, name="donor_login"),
    path("", views.HomeView2.as_view(), name="home"),
]