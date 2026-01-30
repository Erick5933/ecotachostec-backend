from ultralytics import YOLO
from PIL import Image
import numpy as np
from typing import Dict, Any


class LocalClassifier:
    def __init__(self, weights_path: str):
        self.model = YOLO(weights_path)
        # names: dict(int->class_name)
        self.class_names = self.model.names

    def predict_pil(self, image: Image.Image) -> Dict[str, Any]:
        """
        Ejecuta clasificación sobre una imagen PIL y retorna la categoría top-1
        con su confianza (0-100).
        """
        # Ultralytics acepta arrays/paths/PIL
        result = self.model(image)[0]
        # result.probs.top1 returns index; .top1conf returns confidence (0-1)
        top_idx = int(result.probs.top1)
        conf = float(result.probs.top1conf) * 100.0
        label = self.class_names.get(top_idx, str(top_idx)).lower()
        # Además, preparamos top-k (hasta 5)
        top5_idx = result.probs.top5
        top5_conf = result.probs.top5conf
        top_predictions = []
        for i, c in zip(top5_idx, top5_conf):
            name = self.class_names.get(int(i), str(int(i))).lower()
            top_predictions.append({
                "categoria": name,
                "confianza": float(c) * 100.0
            })
        return {
            "label": label,
            "confidence": conf,
            "top": top_predictions
        }
