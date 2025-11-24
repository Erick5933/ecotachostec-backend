# core/urls/deteccion_urls.py
from rest_framework.routers import DefaultRouter
from core.views.deteccion_views import DeteccionViewSet

router = DefaultRouter()
router.register(r"", DeteccionViewSet, basename="detecciones")

urlpatterns = router.urls
