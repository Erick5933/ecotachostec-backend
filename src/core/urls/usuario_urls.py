from rest_framework.routers import DefaultRouter
from core.views.usuario_views import UsuarioViewSet

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet)
urlpatterns = router.urls
