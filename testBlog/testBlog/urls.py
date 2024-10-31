from django.contrib import admin
from django.urls import path, include

from . import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('mainController.urls')),
    path('auth/', include('mainUser.urls'), name='login'),
    path('appointment/', include('appointment.urls'), name='app-admin'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

