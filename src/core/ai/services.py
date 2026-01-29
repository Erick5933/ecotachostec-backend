# src/core/ai/services.py
from PIL import Image
import base64
import io
import logging
import os

from .views import CATEGORY_INFO, resolve_weights_path
from .local_classifier import LocalClassifier

logger = logging.getLogger(__name__)

AI_WEIGHTS = os.getenv('AI_WEIGHTS', '').strip()


def _map_categoria(nombre: str) -> str:
    nombre = (nombre or '').lower().strip()
    mapa = {
        "organicos": "organico",
        "orgánico": "organico",
        "organico": "organico",
        "reciclables": "reciclable",
        "reciclable": "reciclable",
        "inorganicos": "inorganico",
        "inorgánicos": "inorganico",
        "inorganico": "inorganico",
    }
    return mapa.get(nombre, nombre or "inorganico")


def run_ai_detection_from_file(image_file):
    """
    Función reutilizable para detección IA desde una imagen
    (ESP32, backend, tareas, etc.)
    Respeta AI_ENGINE: 'local' usa Ultralytics YOLO, 'roboflow' usa workflow remoto.
    """
    try:
        # Convertir imagen a base64 y PIL (para ambos motores)
        img_pil = Image.open(image_file).convert("RGB")
        buffer = io.BytesIO()
        img_pil.save(buffer, format="JPEG", quality=85)

        img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        # Motor local SIEMPRE (reemplazo definitivo de la IA anterior)
        weights_path = resolve_weights_path()
        if not weights_path or not os.path.exists(weights_path):
            return {
                "success": False,
                "error": "Pesos locales no configurados o no existen. Configure AI_WEIGHTS en entorno.",
            }

        clf = LocalClassifier(weights_path)
        pred = clf.predict_pil(img_pil)
        categoria_std = _map_categoria(pred.get('label', ''))
        info = CATEGORY_INFO.get(categoria_std, CATEGORY_INFO["inorganico"])

        return {
            "success": True,
            "clasificacion_principal": {
                "categoria": categoria_std,
                "confianza": float(pred.get('confidence', 0.0))
            },
            "category_info": info,
            "top_predicciones": pred.get('top', []),
            "tipo": "clasificacion-local"
        }

    except Exception as e:
        logger.exception("Error en IA")
        return {"success": False, "error": str(e)}
