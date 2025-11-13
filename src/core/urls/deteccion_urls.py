from rest_framework.routers import DefaultRouter
from core.views.deteccion_views import DeteccionViewSet

router = DefaultRouter()
router.register(r'detecciones', DeteccionViewSet)
urlpatterns = router.urls
