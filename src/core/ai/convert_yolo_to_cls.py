"""
Convierte un dataset YOLO (detección) a formato de clasificación por carpetas.

Lee labels de YOLO (TXT) y copia cada imagen a la carpeta de la clase
mayoritaria en esa imagen. Usa `data.yaml` para obtener nombres de clases si existe.

Uso:
  python -m core.ai.convert_yolo_to_cls --src "C:/ruta/yolo_dataset" --dst "C:/ruta/cls_dataset"

Estructuras soportadas (en src):
  - train/images/*.jpg, train/labels/*.txt
  - val/images/*.jpg, val/labels/*.txt  (o valid/)
  - test/images/*.jpg, test/labels/*.txt (opcional)

Salida (dst):
  - train/<class_name>/*.jpg
  - val/<class_name>/*.jpg
  - test/<class_name>/*.jpg
"""

import argparse
from pathlib import Path
import shutil
from collections import Counter
import yaml


def load_class_names(data_yaml: Path):
    if data_yaml.is_file():
        with open(data_yaml, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        names = data.get('names')
        if isinstance(names, dict):
            # dict: {0: 'class0', 1: 'class1', ...}
            return {int(k): str(v) for k, v in names.items()}
        if isinstance(names, list):
            return {i: str(n) for i, n in enumerate(names)}
    return {}


def parse_label_file(label_path: Path):
    """Retorna el id de clase mayoritario en el archivo de etiquetas YOLO.
    Cada línea: <class_id> <x_center> <y_center> <width> <height> [<conf>]
    """
    if not label_path.is_file():
        return None
    cls_ids = []
    with open(label_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            try:
                cid = int(float(parts[0]))
                cls_ids.append(cid)
            except Exception:
                continue
    if not cls_ids:
        return None
    return Counter(cls_ids).most_common(1)[0][0]


def convert_split(src_split: Path, dst_base: Path, class_map: dict):
    img_dir = src_split / 'images'
    lbl_dir = src_split / 'labels'
    if not img_dir.is_dir():
        return 0
    count = 0
    for img_path in img_dir.glob('*'):
        if not img_path.suffix.lower() in {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}:
            continue
        label_path = None
        if lbl_dir.is_dir():
            label_path = lbl_dir / (img_path.stem + '.txt')
        cid = parse_label_file(label_path) if label_path else None
        if cid is None:
            # si no hay etiqueta, omitir o enviar a 'unlabeled'
            class_name = 'unlabeled'
        else:
            class_name = class_map.get(cid, str(cid))
        target_dir = dst_base / src_split.name.replace('valid', 'val') / class_name
        target_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(img_path, target_dir / img_path.name)
        count += 1
    return count


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', required=True, help='Raíz del dataset YOLO (contiene train/ val/ test/)')
    ap.add_argument('--dst', required=True, help='Salida en formato clasificación (train/ val/ test/)')
    args = ap.parse_args()

    src = Path(args.src)
    dst = Path(args.dst)
    dst.mkdir(parents=True, exist_ok=True)

    # Cargar nombres de clase desde data.yaml si existe
    class_map = load_class_names(src / 'data.yaml')
    if not class_map:
        class_map = load_class_names(src / 'dataset.yaml')

    total = 0
    for split_name in ['train', 'val', 'valid', 'test']:
        split_dir = src / split_name
        if split_dir.is_dir():
            total += convert_split(split_dir, dst, class_map)

    if total == 0:
        raise RuntimeError('No se encontraron imágenes en formato YOLO (train/val/test con images/labels).')
    print(f'✅ Convertidas {total} imágenes a formato clasificación en: {dst}')


if __name__ == '__main__':
    main()
