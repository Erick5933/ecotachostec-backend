# src/core/ai/services.py
from PIL import Image
import base64
import io
import logging
from .views import detect_with_roboflow, process_roboflow_response

logger = logging.getLogger(__name__)

def run_ai_detection_from_file(image_file):
    """
    Función reutilizable para detección IA desde una imagen
    (ESP32, backend, tareas, etc.)
    """
    try:
        # Convertir imagen a base64
        img_pil = Image.open(image_file).convert("RGB")
        buffer = io.BytesIO()
        img_pil.save(buffer, format="JPEG", quality=85)

        img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        # Llamar a Roboflow
        roboflow_result = detect_with_roboflow(img_base64)

        if not roboflow_result:
            return {"success": False, "error": "Roboflow no respondió"}

        # Procesar resultado
        return process_roboflow_response(roboflow_result)

    except Exception as e:
        logger.exception("Error en IA")
        return {"success": False, "error": str(e)}
