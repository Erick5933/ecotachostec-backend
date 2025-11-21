# core/views/tacho_views.py
from rest_framework import viewsets, permissions
from core.models.tacho_models import Tacho
from core.serializers.tacho_serializers import TachoSerializer
from core.utils.jwt_auth import JWTAuthentication


class TachoViewSet(viewsets.ModelViewSet):
    queryset = Tacho.objects.all()  # pylint: disable=no-member
    serializer_class = TachoSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        user = getattr(self.request, "user", None)

        # Si está autenticado, asignamos automáticamente el usuario
        if user and user.is_authenticated:
            serializer.save(usuario=user)
        else:
            serializer.save()

