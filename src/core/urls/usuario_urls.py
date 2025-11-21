# core/urls/usuario_urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views.usuario_views import UsuarioViewSet, RegisterAPIView, LoginAPIView, ProfileAPIView

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuarios')

urlpatterns = [
    path('auth/register/', RegisterAPIView.as_view()),
    path('auth/login/', LoginAPIView.as_view()),
    path('auth/profile/', ProfileAPIView.as_view()),
]

urlpatterns += router.urls
