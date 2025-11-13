from rest_framework import viewsets
from core.models.usuario_models import Usuario
from core.serializers.usuario_serializers import UsuarioSerializer

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
