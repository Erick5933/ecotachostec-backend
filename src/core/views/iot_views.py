from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils import timezone
import random

from core.models import Tacho, Deteccion


@api_view(["POST"])
@permission_classes([AllowAny])
def esp32_detect(request):
    """
    Endpoint SIMPLIFICADO para ESP32 (sin imagen)
    """

    tacho_id = request.data.get("tacho_id")

    if not tacho_id:
        return Response({"error": "tacho_id requerido"}, status=400)

    try:
        tacho = Tacho.objects.get(id=tacho_id, activo=True)
    except Tacho.DoesNotExist:
        return Response({"error": "Tacho no encontrado"}, status=404)

    # 🔹 SIMULACIÓN DE IA (por ahora)
    categoria = random.choice(["organico", "inorganico", "reciclable"])
    confianza = round(random.uniform(50, 95), 2)

    # 🔹 Guardar detección SIN imagen
    deteccion = Deteccion.objects.create(
        tacho=tacho,
        clasificacion=categoria,
        confianza_ia=confianza,
        imagen=None,
        ubicacion_lat=tacho.ubicacion_lat,
        ubicacion_lon=tacho.ubicacion_lon,
        created_at=timezone.now()
    )

    # 🔹 Parpadeos por tipo
    parpadeos = {
        "organico": 1,
        "inorganico": 2,
        "reciclable": 3
    }.get(categoria, 0)

    return Response({
        "clasificacion": categoria,
        "confianza": confianza,
        "parpadeos": parpadeos,
        "deteccion_id": deteccion.id
    })
