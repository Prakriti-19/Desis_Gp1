from django.contrib import admin
from django.urls import path, include
from inventory.views import  ngoViewSet,donationsViewSet,donorViewSet
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static


router = DefaultRouter()
router.register(r'ngo', ngoViewSet, basename='ngo')
router.register(r'donor', donorViewSet, basename='donor')
router.register(r'donations', donationsViewSet, basename='donations')
# router.register(r'image', ImageViewSet, basename='Image')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('auth1.urls')),
    path('', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)