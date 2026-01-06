from django.urls import path
from rest_framework.routers import DefaultRouter

# 1. Asegúrate de importar TODAS las vistas, incluyendo las nuevas
from core.views.usuario_views import (
    UsuarioViewSet, 
    RegisterAPIView, 
    LoginAPIView, 
    ProfileAPIView,
    GoogleLoginView,            # Nuevo
    RequestPasswordResetEmail,  # Nuevo
    SetNewPasswordAPIView       # Nuevo
)

router = DefaultRouter()
# Esto crea las rutas estándar (GET /usuarios/, POST /usuarios/, etc.)
router.register(r'', UsuarioViewSet, basename='usuarios')

urlpatterns = [
    # Rutas existentes
    path('auth/register/', RegisterAPIView.as_view(), name='register'),
    path('auth/login/', LoginAPIView.as_view(), name='login'),
    path('auth/profile/', ProfileAPIView.as_view(), name='profile'),
    
    # 2. Nuevas Rutas
    path('auth/google/', GoogleLoginView.as_view(), name='google-login'),
    path('auth/request-reset-email/', RequestPasswordResetEmail.as_view(), name='request-reset-email'),
    path('auth/password-reset-complete/', SetNewPasswordAPIView.as_view(), name='password-reset-complete'),
]

urlpatterns += router.urls