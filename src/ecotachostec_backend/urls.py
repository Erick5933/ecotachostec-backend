# src/ecotachostec_backend/urls.py

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# IMPORTAR VIEWSETS
from core.views.tacho_views import TachoViewSet
from core.views.deteccion_views import DeteccionViewSet
from core.views.ubicacion_views import ProvinciaViewSet, CiudadViewSet, CantonViewSet

# Crear router principal
router = DefaultRouter()
router.register(r'tachos', TachoViewSet)
router.register(r'detecciones', DeteccionViewSet)
router.register(r'provincias', ProvinciaViewSet)
router.register(r'ciudades', CiudadViewSet)
router.register(r'cantones', CantonViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),

    # Rutas personalizadas de usuarios
    path("api/", include("core.urls.usuario_urls")),

    # Rutas automáticas de los routers DRF (tachos, detecciones, ubicaciones)
    path("api/", include(router.urls)),
    
    
]
