from rest_framework.routers import DefaultRouter
from core.views.ubicacion_views import ProvinciaViewSet, CiudadViewSet, CantonViewSet

router = DefaultRouter()
router.register(r'provincias', ProvinciaViewSet)
router.register(r'ciudades', CiudadViewSet)
router.register(r'cantones', CantonViewSet)

urlpatterns = router.urls
