from django.contrib import admin
from django.urls import path, include
from inventory.views import  donationsViewSet
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static


router = DefaultRouter()
router.register(r'donations', donationsViewSet, basename='donations')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('', include('auth1.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)