import os
from roboflow import Roboflow

API_KEY = os.getenv("ROBOFLOW_API_KEY", "")
WORKSPACE = os.getenv("ROBOFLOW_WORKSPACE", "frosdh")
PROJECT = os.getenv("ROBOFLOW_PROJECT", "ia-final-uof7b")
VERSION = int(os.getenv("ROBOFLOW_VERSION", "4"))
FORMAT = os.getenv("ROBOFLOW_FORMAT", "folder")  # e.g., "folder", "coco", "yolov5"
OUTPUT_DIR = os.getenv("ROBOFLOW_OUTPUT_DIR", f"datasets/{PROJECT}-v{VERSION}")

if not API_KEY:
    raise RuntimeError("ROBOFLOW_API_KEY no está configurada en el entorno")

print(f"Descargando dataset: workspace={WORKSPACE} project={PROJECT} version={VERSION} format={FORMAT}")
rf = Roboflow(api_key=API_KEY)
project = rf.workspace(WORKSPACE).project(PROJECT)
version = project.version(VERSION)

# Esto descargará y extraerá el dataset en OUTPUT_DIR
# Para formatos distintos, asegúrate de que el backend que entrenará lo soporte
os.makedirs(OUTPUT_DIR, exist_ok=True)

dataset = version.download(FORMAT, location=OUTPUT_DIR)
print(f"✅ Dataset descargado en: {dataset.location}")
