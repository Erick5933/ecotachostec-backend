from rest_framework.routers import DefaultRouter
from core.views.tacho_views import TachoViewSet

router = DefaultRouter()
router.register(r'tachos', TachoViewSet)
urlpatterns = router.urls
