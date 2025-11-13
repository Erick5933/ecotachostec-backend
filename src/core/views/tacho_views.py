from rest_framework import viewsets
from core.models.tacho_models import Tacho
from core.serializers.tacho_serializers import TachoSerializer

class TachoViewSet(viewsets.ModelViewSet):
    queryset = Tacho.objects.all()
    serializer_class = TachoSerializer
