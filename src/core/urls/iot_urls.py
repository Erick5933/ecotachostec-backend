from django.urls import path
from core.views.iot_views import esp32_detect

urlpatterns = [
    path("esp32/detect/", esp32_detect, name="esp32-detect"),
]
