# core/views/deteccion_views.py
from rest_framework import viewsets, permissions
from core.models.deteccion_models import Deteccion
from core.serializers.deteccion_serializers import DeteccionSerializer
from core.utils.jwt_auth import JWTAuthentication

class DeteccionViewSet(viewsets.ModelViewSet):
    queryset = Deteccion.objects.all()  # pylint: disable=no-member
    serializer_class = DeteccionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # opcional: verificar tacho existente o asignar datos adicionales
        serializer.save()
