# core/views/tacho_views.py
from rest_framework import viewsets, permissions
from core.models.tacho_models import Tacho
from core.serializers.tacho_serializers import TachoSerializer
from core.utils.jwt_auth import JWTAuthentication


class TachoViewSet(viewsets.ModelViewSet):
    queryset = Tacho.objects.all()
    serializer_class = TachoSerializer
    authentication_classes = [JWTAuthentication]

    # Permite leer sin autenticación, pero crear solo si tiene token
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # Como el modelo Tacho NO tiene usuario, simplemente guardamos
        serializer.save()
