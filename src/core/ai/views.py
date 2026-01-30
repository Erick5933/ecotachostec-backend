# src/core/ai/views.py
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils import timezone
from PIL import Image
import logging
import base64
import io
import requests
import os
from pathlib import Path

from .local_classifier import LocalClassifier

logger = logging.getLogger(__name__)
def resolve_weights_path() -> str:
    """Resuelve la ruta del modelo .pt.

    1) Usa AI_WEIGHTS del entorno si existe.
    2) Busca automáticamente en <repo_root>/runs/classify/**/weights/best.pt y retorna el más reciente.
    """
    if AI_ENGINE != 'local':
        return ''

    if AI_WEIGHTS and os.path.exists(AI_WEIGHTS):
        return AI_WEIGHTS

    try:
        repo_root = Path(__file__).resolve().parents[3]  # .../ecotachostec-backend2
        candidates = list(repo_root.glob('runs/classify/**/weights/best.pt'))
        if not candidates:
            return ''
        # elegir el más reciente por mtime
        latest = max(candidates, key=lambda p: p.stat().st_mtime)
        return str(latest)
    except Exception:
        return ''


# ==================== CONFIGURACIÓN IA ====================
AI_ENGINE = os.getenv('AI_ENGINE', 'local').lower()  # 'roboflow' | 'local'
AI_WEIGHTS = os.getenv('AI_WEIGHTS', '').strip()  # Ruta a pesos locales (.pt) si AI_ENGINE='local'

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
    """
    Llama al workflow de Roboflow con la imagen en base64
    """
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

# ==================== FUNCIÓN MEJORADA PARA PROCESAR RESPUESTA ====================
def process_roboflow_response(roboflow_result):
    """
    Procesa la respuesta del workflow de Roboflow.
    Maneja el caso donde no se detecta nada (predictions: [])
    """
    try:
        logger.info("🔍 Procesando respuesta de Roboflow...")
        
        # Verificar estructura de outputs
        outputs = roboflow_result.get("outputs", [])
        if not outputs:
            logger.warning("⚠️ No hay 'outputs' en la respuesta")
            return {
                "success": False,
                "no_detection": True,
                "message": "No se detectaron objetos en la imagen",
                "suggestions": [
                    "Asegúrate de que el objeto esté bien iluminado",
                    "Intenta acercar más la cámara al objeto",
                    "Verifica que el objeto esté en el centro de la imagen",
                    "La imagen debe contener un residuo visible"
                ]
            }
        
        logger.info(f"📦 Se encontraron {len(outputs)} outputs")
        
        # Buscar predicciones en diferentes estructuras
        all_predictions = []
        
        for idx, output in enumerate(outputs):
            logger.info(f"🔎 Analizando output {idx}: {list(output.keys())}")
            
            # Estructura 1: output.predictions.predictions[]
            if "predictions" in output:
                pred_data = output["predictions"]
                
                # Si predictions es un dict con predictions dentro
                if isinstance(pred_data, dict) and "predictions" in pred_data:
                    preds = pred_data["predictions"]
                    logger.info(f"✅ Encontradas {len(preds)} predicciones en output.predictions.predictions")
                    all_predictions.extend(preds)
                
                # Si predictions es directamente una lista
                elif isinstance(pred_data, list):
                    logger.info(f"✅ Encontradas {len(pred_data)} predicciones en output.predictions")
                    all_predictions.extend(pred_data)
            
            # Estructura 2: output.detections[]
            if "detections" in output and isinstance(output["detections"], list):
                logger.info(f"✅ Encontradas {len(output['detections'])} detecciones")
                all_predictions.extend(output["detections"])
            
            # Estructura 3: output.top[] (clasificación)
            if "top" in output and isinstance(output["top"], list):
                logger.info(f"✅ Encontradas {len(output['top'])} clasificaciones top")
                all_predictions.extend(output["top"])
        
        # ⚠️ CASO CRÍTICO: No hay predicciones (array vacío)
        if not all_predictions or len(all_predictions) == 0:
            logger.warning("⚠️ No se encontraron predicciones - El modelo no detectó ningún objeto")
            return {
                "success": False,
                "no_detection": True,
                "message": "No se detectaron objetos en la imagen",
                "suggestions": [
                    "Asegúrate de que el objeto esté bien iluminado",
                    "Intenta acercar más la cámara al objeto",
                    "Verifica que el objeto esté en el centro de la imagen",
                    "La imagen debe contener un residuo claramente visible"
                ],
                "roboflow_raw": roboflow_result
            }
        
        logger.info(f"📊 Total de predicciones encontradas: {len(all_predictions)}")
        
        # Ordenar por confianza
        sorted_predictions = sorted(
            all_predictions, 
            key=lambda x: float(x.get('confidence', x.get('score', 0))), 
            reverse=True
        )
        
        # Obtener la predicción principal
        principal = sorted_predictions[0]
        logger.info(f"🎯 Predicción principal: {principal}")
        
        # Extraer la categoría (probar múltiples campos)
        categoria = (
            principal.get("class") or
            principal.get("predicted_class") or
            principal.get("label") or
            principal.get("class_name")
        )
        
        if not categoria:
            logger.error(f"❌ No se pudo extraer la clase de: {principal}")
            return {
                "success": False,
                "no_detection": True,
                "message": "No se pudo identificar la categoría del objeto",
                "roboflow_raw": roboflow_result
            }
        
        # Extraer confianza
        confianza = float(
            principal.get("confidence", 
            principal.get("score", 
            principal.get("prob", 0.0)))
        ) * 100
        
        categoria_lower = categoria.lower().strip()
        
        # Mapear categoría si es necesario
        categoria_map = {
            "organicos": "organico",
            "orgánico": "organico",
            "reciclables": "reciclable",
            "inorganicos": "inorganico",
            "inorgánicos": "inorganico"
        }
        categoria_lower = categoria_map.get(categoria_lower, categoria_lower)
        
        logger.info(f"✅ Clasificación exitosa: {categoria_lower} ({confianza:.2f}%)")
        
        # Preparar top predicciones
        top_predicciones = []
        for pred in sorted_predictions[:5]:
            cat = (pred.get("class") or pred.get("predicted_class") or pred.get("label") or "").lower()
            cat = categoria_map.get(cat, cat)
            conf = float(pred.get("confidence", pred.get("score", 0))) * 100
            
            if cat and cat in CATEGORY_INFO:
                top_predicciones.append({
                    "categoria": cat,
                    "confianza": conf
                })
        
        # Obtener información de la categoría
        category_info = CATEGORY_INFO.get(categoria_lower, CATEGORY_INFO["inorganico"])
        
        return {
            "success": True,
            "clasificacion_principal": {
                "categoria": categoria_lower,
                "confianza": confianza
            },
            "category_info": category_info,
            "top_predicciones": top_predicciones,
            "tipo": "clasificacion",
            "roboflow_raw": roboflow_result  # Para debugging
        }
        
    except Exception as e:
        logger.exception(f"💥 Error procesando respuesta de Roboflow: {str(e)}")
        return {
            "success": False,
            "error": f"Error procesando respuesta: {str(e)}",
            "roboflow_raw": roboflow_result
        }

# ==================== ENDPOINTS ====================
@api_view(['GET'])
@permission_classes([AllowAny])
def ai_health(request):
    """Verifica el estado del servicio de IA"""
    payload = {
        'status': 'operational',
        'engine': AI_ENGINE,
        'service': f"EcoTachosTec IA - {'Local (Ultralytics)' if AI_ENGINE=='local' else 'Roboflow'}",
        'timestamp': timezone.now().isoformat(),
    }

    if AI_ENGINE == 'local':
        resolved = resolve_weights_path()
        chosen = resolved or AI_WEIGHTS
        payload.update({
            'message': '✅ Motor local listo',
            'weights': chosen,
            'weights_exists': bool(chosen) and os.path.exists(chosen),
            'categories': list(CATEGORY_INFO.keys()),
        })
    else:
        try:
            response = requests.get(ROBOFLOW_CONFIG['api_url'], timeout=5)
            roboflow_available = response.status_code == 200
        except Exception:
            roboflow_available = False
        payload.update({
            'roboflow_available': roboflow_available,
            'workspace': ROBOFLOW_CONFIG['workspace'],
            'workflow_id': ROBOFLOW_CONFIG['workflow_id'],
            'message': '✅ Conectado a Roboflow' if roboflow_available else '⚠️ Roboflow no disponible',
        })

    return JsonResponse(payload)

@api_view(['POST'])
@permission_classes([AllowAny])
def ai_detect(request):
    """
    Endpoint principal para detectar/clasificar residuos
    - roboflow: usa workflow remoto
    - local: usa clasificador Ultralytics
    """
    try:
        imagen = None

        # 1️⃣ Obtener imagen desde request.FILES
        if request.FILES:
            for key in request.FILES:
                imagen = request.FILES[key]
                logger.info(f"📸 Imagen recibida desde FILES: {key}")
                break

        # 2️⃣ Obtener imagen desde request.data (base64)
        if not imagen and hasattr(request, 'data'):
            imagen_data = request.data.get('imagen')
            if isinstance(imagen_data, str) and imagen_data.startswith('data:image'):
                try:
                    imagen_bytes = base64.b64decode(imagen_data.split(',')[1])
                    imagen = io.BytesIO(imagen_bytes)
                    logger.info("📸 Imagen recibida desde base64")
                except Exception as e:
                    return Response({
                        "success": False,
                        "error": f"Error decodificando imagen base64: {str(e)}"
                    }, status=400)

        if not imagen:
            logger.warning("❌ No se recibió imagen")
            return Response({
                "success": False,
                "error": "No se envió imagen. Enviar archivo en 'imagen' o base64"
            }, status=400)

        # 3️⃣ Convertir imagen a base64 para Roboflow
        try:
            img_pil = Image.open(imagen).convert('RGB')
            buffered = io.BytesIO()
            img_pil.save(buffered, format="JPEG", quality=85)
            img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            logger.info(f"🖼️ Imagen convertida a base64 ({len(img_base64)} chars)")
        except Exception as e:
            logger.error(f"Error procesando imagen: {str(e)}")
            return Response({
                "success": False,
                "error": f"Error procesando imagen: {str(e)}"
            }, status=400)

        # Motor local SIEMPRE (reemplazo definitivo)
        weights_path = resolve_weights_path()
        if not weights_path or not os.path.exists(weights_path):
            return Response({
                "success": False,
                "error": "Pesos locales no configurados. Defina AI_WEIGHTS en el entorno."
            }, status=500)

        clf = LocalClassifier(weights_path)
        img_pil = Image.open(io.BytesIO(base64.b64decode(img_base64))).convert('RGB')
        pred = clf.predict_pil(img_pil)
        categoria = pred['label']
        confianza = pred['confidence']

        categoria_map = {
            "organicos": "organico",
            "orgánico": "organico",
            "organico": "organico",
            "reciclables": "reciclable",
            "reciclable": "reciclable",
            "inorganicos": "inorganico",
            "inorgánicos": "inorganico",
            "inorganico": "inorganico",
        }
        categoria_std = categoria_map.get(categoria.lower(), categoria.lower())
        category_info = CATEGORY_INFO.get(categoria_std, CATEGORY_INFO["inorganico"])

        return Response({
            "success": True,
            "clasificacion_principal": {
                "categoria": categoria_std,
                "confianza": confianza
            },
            "category_info": category_info,
            "top_predicciones": pred["top"],
            "tipo": "clasificacion-local"
        })

    except Exception as e:
        logger.exception(f"💥 Error crítico en ai_detect: {str(e)}")
        return Response({
            "success": False,
            "error": f"Error interno procesando la imagen: {str(e)}"
        }, status=500)

# Alias para compatibilidad
@api_view(['POST'])
@permission_classes([AllowAny])
def detectar_basura(request):
    return ai_detect(request)

@api_view(['GET'])
@permission_classes([AllowAny])
def ai_model_info(request):
    """Información sobre el modelo de IA"""
    if AI_ENGINE == 'local':
        resolved = resolve_weights_path()
        chosen = resolved or AI_WEIGHTS
        model_info = {
            'type': 'local_ultralytics',
            'weights': chosen,
            'categories': list(CATEGORY_INFO.keys()),
            'available': bool(chosen) and os.path.exists(chosen),
        }
    else:
        model_info = {
            'type': 'roboflow_workflow',
            'workspace': ROBOFLOW_CONFIG['workspace'],
            'workflow_id': ROBOFLOW_CONFIG['workflow_id'],
            'categories': list(CATEGORY_INFO.keys()),
            'available': True,
        }

    return JsonResponse({
        'success': True,
        'engine': AI_ENGINE,
        'model': model_info,
        'timestamp': timezone.now().isoformat(),
    })

# Compatibilidad con nombres antiguos
WasteAnalysisView = ai_detect
ModelStatusView = ai_health