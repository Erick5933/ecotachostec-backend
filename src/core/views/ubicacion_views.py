from rest_framework import viewsets
from core.models.ubicacion_models import Provincia, Ciudad, Canton
from core.serializers.ubicacion_serializers import ProvinciaSerializer, CiudadSerializer, CantonSerializer

class ProvinciaViewSet(viewsets.ModelViewSet):
    queryset = Provincia.objects.all()
    serializer_class = ProvinciaSerializer

class CiudadViewSet(viewsets.ModelViewSet):
    queryset = Ciudad.objects.all()
    serializer_class = CiudadSerializer

class CantonViewSet(viewsets.ModelViewSet):
    queryset = Canton.objects.all()
    serializer_class = CantonSerializer
