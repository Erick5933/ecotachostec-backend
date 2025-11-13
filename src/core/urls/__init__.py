from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls.usuario_urls')),
    path('api/', include('core.urls.ubicacion_urls')),
    path('api/', include('core.urls.tacho_urls')),
    path('api/', include('core.urls.deteccion_urls')),
]
