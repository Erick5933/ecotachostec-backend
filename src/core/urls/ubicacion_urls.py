# core/urls/ubicacion_urls.py
from rest_framework.routers import DefaultRouter
from core.views.ubicacion_views import ProvinciaViewSet, CiudadViewSet, CantonViewSet

router = DefaultRouter()
router.register(r"provincias", ProvinciaViewSet, basename="provincias")
router.register(r"ciudades", CiudadViewSet, basename="ciudades")
router.register(r"cantones", CantonViewSet, basename="cantones")

urlpatterns = router.urls
