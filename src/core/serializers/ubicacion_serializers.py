from rest_framework import serializers
from core.models.ubicacion_models import Provincia, Ciudad, Canton

class ProvinciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provincia
        fields = '__all__'

class CiudadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ciudad
        fields = '__all__'

class CantonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Canton
        fields = '__all__'
