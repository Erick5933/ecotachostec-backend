# src/core/ai/services.py - VERSIÓN SOLO ROBOFLOW
from PIL import Image
import base64
import io
import logging
import requests

logger = logging.getLogger(__name__)

# ==================== CONFIGURACIÓN ROBOFLOW ====================
ROBOFLOW_CONFIG = {
    'api_url': 'https://serverless.roboflow.com',
    'api_key': 'T02OsUf25gIOG7id3A9r',
    'workspace': 'frosdh',
    'workflow_id': 'find-inorganicos-reciclables-and-organicos-2'
}

CATEGORY_INFO = {
    "organico": {
        "label": "ORGÁNICO", "icon": "🌱", "color": "#10b981", "bgColor": "#d1fae5",
        "description": "Residuo orgánico - Depositar en contenedor verde",
        "examples": "Restos de comida, cáscaras, residuos vegetales"
    },
    "reciclable": {
        "label": "RECICLABLE", "icon": "♻️", "color": "#3b82f6", "bgColor": "#dbeafe",
        "description": "Material reciclable - Depositar en contenedor azul",
        "examples": "Plástico, papel, cartón, vidrio, metal"
    },
    "inorganico": {
        "label": "INORGÁNICO", "icon": "🗑️", "color": "#6b7280", "bgColor": "#f3f4f6",
        "description": "Residuo no reciclable - Depositar en contenedor gris",
        "examples": "Residuos no reciclables, desechos diversos"
    }
}

# ==================== FUNCIÓN PARA LLAMAR A ROBOFLOW ====================
def detect_with_roboflow(image_base64):
    """Llama a Roboflow con la imagen en base64"""
    try:
        url = f"{ROBOFLOW_CONFIG['api_url']}/{ROBOFLOW_CONFIG['workspace']}/workflows/{ROBOFLOW_CONFIG['workflow_id']}"
        
        payload = {
            "api_key": ROBOFLOW_CONFIG['api_key'],
            "inputs": {
                "image": {
                    "type": "base64",
                    "value": image_base64
                }
            }
        }
        
        headers = {"Content-Type": "application/json"}
        
        logger.info(f"🚀 Llamando a Roboflow workflow: {ROBOFLOW_CONFIG['workflow_id']}")
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        logger.info(f"📡 Status Code de Roboflow: {response.status_code}")
        
        if response.status_code != 200:
            logger.error(f"❌ Roboflow error {response.status_code}: {response.text}")
            return None
            
        result = response.json()
        logger.info(f"✅ Respuesta de Roboflow recibida")
        
        return result
        
    except requests.exceptions.Timeout:
        logger.error("⏰ Timeout al conectar con Roboflow")
        return None
    except Exception as e:
        logger.exception(f"💥 Error en Roboflow: {str(e)}")
        return None

# ==================== FUNCIÓN PARA PROCESAR RESPUESTA ====================
def process_roboflow_response(roboflow_result):
    """Procesa respuesta de Roboflow"""
    if not roboflow_result:
        return {"success": False, "error": "No response from Roboflow"}
    
    try:
        outputs = roboflow_result.get("outputs", [])
        if not outputs:
            return {
                "success": False,
                "no_detection": True,
                "message": "No se detectaron objetos"
            }
        
        # Extraer todas las predicciones
        all_predictions = []
        for output in outputs:
            if "predictions" in output:
                preds = output["predictions"]
                if isinstance(preds, dict) and "predictions" in preds:
                    all_predictions.extend(preds["predictions"])
                elif isinstance(preds, list):
                    all_predictions.extend(preds)
        
        if not all_predictions:
            return {
                "success": False,
                "no_detection": True,
                "message": "No se detectaron objetos en la imagen"
            }
        
        # Obtener mejor predicción
        best_pred = max(all_predictions, key=lambda x: float(x.get('confidence', 0)))
        categoria = best_pred.get("class", "").lower()
        confianza = float(best_pred.get("confidence", 0)) * 100
        
        # Mapear categoría
        categoria_map = {
            "organicos": "organico", "orgánico": "organico",
            "reciclables": "reciclable",
            "inorganicos": "inorganico", "inorgánicos": "inorganico"
        }
        categoria_final = categoria_map.get(categoria, categoria)
        
        return {
            "success": True,
            "clasificacion_principal": {
                "categoria": categoria_final,
                "confianza": confianza
            },
            "category_info": CATEGORY_INFO.get(categoria_final, CATEGORY_INFO["inorganico"])
        }
        
    except Exception as e:
        logger.exception(f"Error procesando respuesta: {str(e)}")
        return {"success": False, "error": str(e)}

# ==================== FUNCIÓN PRINCIPAL ====================
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