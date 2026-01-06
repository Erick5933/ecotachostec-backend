from django.urls import path, include

urlpatterns = [
    path("usuarios/", include("core.urls.usuario_urls")),
    path("ubicacion/", include("core.urls.ubicacion_urls")),
    path("tachos/", include("core.urls.tacho_urls")),
    path("detecciones/", include("core.urls.deteccion_urls")),
    path("iot/", include("core.urls.iot_urls")),   # 👈 AÑADIR
]
