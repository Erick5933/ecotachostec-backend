# core/urls/tacho_urls.py
from rest_framework.routers import DefaultRouter
from core.views.tacho_views import TachoViewSet

router = DefaultRouter()
router.register(r"", TachoViewSet, basename="tachos")

urlpatterns = router.urls
