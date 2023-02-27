from . import views
from django.urls import path
from inventory.views import DonationView

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("donate/", DonationView.as_view(), name="add_donation"),
    path("", views.HomeView.as_view(), name="home"),
]