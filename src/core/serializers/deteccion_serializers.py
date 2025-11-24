from rest_framework import serializers
from core.models.deteccion_models import Deteccion

class DeteccionSerializer(serializers.ModelSerializer):
    tacho_nombre = serializers.CharField(source="tacho.nombre", read_only=True)

    class Meta:
        model = Deteccion
        fields = "__all__"  # incluye todo lo normal
        extra_fields = ["tacho_nombre"]
