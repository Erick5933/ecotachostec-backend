from rest_framework import viewsets
from core.models.deteccion_models import Deteccion
from core.serializers.deteccion_serializers import DeteccionSerializer

class DeteccionViewSet(viewsets.ModelViewSet):
    queryset = Deteccion.objects.all()
    serializer_class = DeteccionSerializer
