# src/ecotachostec_backend/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    # Todas las rutas de la API (usuarios, tachos, detecciones, ubicaciones)
    path("api/", include("core.urls")),
]
