from rest_framework import serializers
from core.models.deteccion_models import Deteccion

class DeteccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deteccion
        fields = '__all__'
