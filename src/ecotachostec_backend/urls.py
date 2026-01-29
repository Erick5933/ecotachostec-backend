# src/ecotachostec_backend/urls.py
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Configuración de Swagger
schema_view = get_schema_view(
   openapi.Info(
      title="EcoTachosTec API",
      default_version='v1',
      description="API para gestión de tachos inteligentes con clasificación de basura mediante IA",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="kawsana375@gmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),

    # Documentación Swagger/OpenAPI
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Todas las rutas de la API (usuarios, tachos, detecciones, ubicaciones)
    path("api/", include("core.urls")),

      # IA (NO TOCAR)
    path("api/ia/", include("core.ai.urls")),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
