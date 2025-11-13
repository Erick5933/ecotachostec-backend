from rest_framework import serializers
from core.models.tacho_models import Tacho

class TachoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tacho
        fields = '__all__'
