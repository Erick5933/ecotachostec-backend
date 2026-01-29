# core/urls/ubicacion_urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter
from core.views.ubicacion_views import (
    ProvinciaViewSet, CiudadViewSet, CantonViewSet,
    autocompletar_provincia, autocompletar_ciudad, autocompletar_canton,
    guardar_ubicacion_smart
)

router = DefaultRouter()
router.register(r"provincias", ProvinciaViewSet, basename="provincias")
router.register(r"ciudades", CiudadViewSet, basename="ciudades")
router.register(r"cantones", CantonViewSet, basename="cantones")

urlpatterns = [
    # Autocompletado
    path('autocompletar-provincia/', autocompletar_provincia, name='autocompletar-provincia'),
    path('autocompletar-ciudad/', autocompletar_ciudad, name='autocompletar-ciudad'),
    path('autocompletar-canton/', autocompletar_canton, name='autocompletar-canton'),
    
    # Guardar ubicación inteligente
    path('guardar/', guardar_ubicacion_smart, name='guardar-ubicacion'),
] + router.urls
