from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from core.models import Tacho
# ⚠️ MEMORIA TEMPORAL (prototipo)
ORDENES_PENDIENTES = {}


@api_view(["POST"])
@permission_classes([AllowAny])
def esp32_detect(request):
    print("📡 ESP32 DETECT LLAMADO")
    print("📥 DATA RECIBIDA:", request.data)

    tacho_id = request.data.get("tacho_id")
    clasificacion = request.data.get("clasificacion")

    if not tacho_id:
        return Response({"error": "tacho_id requerido"}, status=400)

    # 🔹 CASO 1: FRONTEND manda clasificación
    if clasificacion:
        clasificacion = clasificacion.lower().strip()

        parpadeos = {
            "organico": 1,
            "inorganico": 2,
            "reciclable": 3,
        }.get(clasificacion, 0)

        # ✅ GUARDAR ORDEN
        ORDENES_PENDIENTES[tacho_id] = parpadeos

        print("🧠 CLASIFICACIÓN:", clasificacion)
        print("💾 ORDEN GUARDADA:", parpadeos)

        return Response({
            "ok": True,
            "parpadeos": parpadeos,
        })

    # 🔹 CASO 2: ESP32 pregunta
    parpadeos = ORDENES_PENDIENTES.pop(tacho_id, 0)

    print("🤖 ESP32 consulta")
    print("📤 ORDEN ENTREGADA:", parpadeos)

    return Response({
        "ok": True,
        "parpadeos": parpadeos,
    })
