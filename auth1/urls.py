from . import views
from django.urls import path
# from auth1.views import MyObtainTokenPairView, RegisterView
# from rest_framework_simplejwt.views import TokenRefreshView


# urlpatterns = [
#     path('login/', MyObtainTokenPairView.as_view(), name='token_obtain_pair'),
#     path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
#     path('', RegisterView.as_view(), name='auth_register'),
# ]
urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
]