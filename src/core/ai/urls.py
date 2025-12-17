# src/core/ai/urls.py
from django.urls import path
from . import views  # Importa el módulo views completo

urlpatterns = [
    # Health check
    path('health/', views.ai_health, name='ai-health'),
    
    # Detección de residuos
    path('detect/', views.ai_detect, name='ai-detect'),
    
    # Información del modelo
    path('info/', views.ai_model_info, name='ai-info'),
    
    # Para compatibilidad con tu código anterior
    path('analizar/', views.ai_detect, name='analizar_imagen'),
    path('status/', views.ai_health, name='model_status'),
]