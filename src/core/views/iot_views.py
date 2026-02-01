from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.core.files.base import ContentFile
import base64

# IMPORTS DE TUS MODELOS
from core.models.tacho_models import Tacho
from core.models.deteccion_models import Deteccion

# IMPORTS DE TU IA (ROBOFLOW)
from core.ai.services import run_ai_detection_from_file

# ⚠️ MEMORIA TEMPORAL
ORDENES_PENDIENTES = {}


@api_view(["POST"])
@permission_classes([AllowAny])
def esp32_detect(request):
    print("📡 ESP32 DETECT LLAMADO (Backend)")
    
    tacho_id = request.data.get("tacho_id")
    clasificacion_final = "ninguno"
    imagen_file = request.FILES.get("imagen") 
    confianza = 0.0  # valor por defecto

    if not tacho_id:
        return Response({"error": "tacho_id requerido"}, status=400)

    # 🔹 PASO 1: PROCESAR IMAGEN CON ROBOFLOW
    if imagen_file:
        print("🧠 Procesando imagen con Roboflow...")
        try:
            resultado_ia = run_ai_detection_from_file(imagen_file)
            imagen_file.seek(0)

            if resultado_ia.get("success", False):
                clasificacion_final = resultado_ia["clasificacion_principal"]["categoria"]
                confianza = resultado_ia["clasificacion_principal"]["confianza"]
                print(f"🤖 Roboflow dice: {clasificacion_final} ({confianza}%)")
            else:
                print(f"⚠️ IA falló: {resultado_ia.get('message', 'Error desconocido')}")
                clasificacion_final = "ninguno"
                confianza = 0.0
        except Exception as e:
            print(f"❌ Error invocando servicio IA: {e}")
            clasificacion_final = "ninguno"
            confianza = 0.0
    else:
        print("⚠️ No llegó imagen, usando clasificación manual si existe")
        clasificacion_final = request.data.get("clasificacion", "ninguno")
        confianza = 0.0

    # 🔹 PASO 2: GUARDAR EN BASE DE DATOS
    tacho = Tacho.objects.filter(id=tacho_id).first()
    
    if tacho:
        try:
            lat = getattr(tacho, 'latitud', 0.0) 
            lon = getattr(tacho, 'longitud', 0.0)
            if lat is None: lat = 0.0
            if lon is None: lon = 0.0

            nueva_deteccion = Deteccion(
                tacho=tacho,
                clasificacion=clasificacion_final, 
                ubicacion_lat=lat,
                ubicacion_lon=lon,
                confianza_ia=confianza,  # <-- ahora guarda el porcentaje real
                activo=True,
                procesado=True
            )

            if imagen_file:
                nueva_deteccion.imagen = imagen_file
            
            nueva_deteccion.save() 
            print(f"✅ Detección guardada en BD: ID {nueva_deteccion.id} - {clasificacion_final} ({confianza}%)")
        
        except Exception as e:
            print(f"❌ Error guardando en BD: {e}")
    else:
        print("❌ Tacho no encontrado en BD")

    # 🔹 PASO 3: DETERMINAR MOVIMIENTO DEL MOTOR
    parpadeos = {
        "organico": 1,
        "inorganico": 2,
        "reciclable": 3,
        "plastico": 3,
        "papel": 3,
        "botella": 3
    }.get(clasificacion_final, 0)
    
    ORDENES_PENDIENTES[tacho_id] = parpadeos

    return Response({
        "ok": True,
        "mensaje": "Procesado con IA",
        "clasificacion_ia": clasificacion_final,
        "confianza_ia": confianza,  # <-- también lo devuelvo en la respuesta
        "parpadeos": parpadeos,
    })
