from . import views
from django.urls import path
from inventory.views import *
from auth1.views import *
from payment.views import *


urlpatterns = [
    path(
        "update_donation_status/",
        update_donation_status_donor,
        name="update_donation_status_donor",
    ),
    path(
        "update_donation_status_ngo/",
        update_donation_status_ngo,
        name="update_donation_status_ngo",
    ),
    path("logout/", logout_view, name="logout"),
    path("donate/", donate, name="add_donation"),
    path("ngo_list/", ngo_list, name="ngo_list"),
    path("stats/", donations_stats, name="stats"),
    path("ngo_stats/", ngo_stats, name="ngo_stats"),
    path("process-payment/", process_payment, name="process_payment"),
    path("list/", donations_list, name="donations_list"),
    path("donor_history/", donor_history, name="donor_history"),
    path("redeem_points/", redeem_points, name="redeem_points"),
    path("donate_points/", donate_points, name="donate_points"),
    path("pay/", pay, name="pay"),
    path("mail/<email>/", mail, name="mail"),
    path("donate_points/<int:ngo_id>/", donate_points, name="donate_points"),
    path("ngo_register/", views.NgoSignUpView.as_view(), name="ngo_register"),
    path("donor_register/", views.DonorSignUpView.as_view(), name="donor_register"),
    path("ngo_login/", ngo_login_view, name="ngo_login"),
    path("donor_login/", donor_login_view, name="donor_login"),
    path("ngo_home/", ngo_home, name="ngo_home"),
    path("donor_home/", donor_home, name="donor_home"),
    path("", home_view, name="home"),
]
