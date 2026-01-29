"""
Entrenamiento rápido de clasificación con Ultralytics YOLO (v8) usando transferencia de aprendizaje.

Estructura esperada del dataset (ImageNet-like):
dataset_dir/
	train/
		clase1/
		clase2/
	val/
		clase1/
		clase2/
	test/   (opcional)
		clase1/
		clase2/

Uso:
	python -m core.ai.train --data C:/ruta/dataset --model yolov8n-cls.pt --epochs 30 --imgsz 224
"""

import argparse
from ultralytics import YOLO


def train(data_dir: str, model_name: str = "yolov8n-cls.pt", epochs: int = 30, imgsz: int = 224):
		model = YOLO(model_name)
		results = model.train(data=data_dir, epochs=epochs, imgsz=imgsz)
		return results


def main():
		parser = argparse.ArgumentParser()
		parser.add_argument('--data', required=True, help='Directorio del dataset (con train/ y val/)')
		parser.add_argument('--model', default='yolov8n-cls.pt', help='Modelo base (yolov8n-cls.pt, yolov8s-cls.pt, etc.)')
		parser.add_argument('--epochs', type=int, default=30)
		parser.add_argument('--imgsz', type=int, default=224)
		args = parser.parse_args()

		train(args.data, args.model, args.epochs, args.imgsz)


if __name__ == '__main__':
		main()

