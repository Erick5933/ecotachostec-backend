"""
Utilidad para preparar dataset de clasificación en formato ImageNet (train/val/test por clase).

Ejemplo de uso:
  python -m core.ai.prepare_dataset --src "C:/ruta/dataset_origen" --dst "C:/ruta/dataset_split" --val 0.1 --test 0.1

El origen debe tener subcarpetas por clase, por ejemplo:
  dataset_origen/
    organico/
    reciclable/
    inorganico/

Se copiarán imágenes a:
  dataset_split/
    train/<clase>/
    val/<clase>/
    test/<clase>/
"""

import argparse
import os
import shutil
from pathlib import Path
from typing import List
import random

IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def list_images(folder: Path) -> List[Path]:
    return [p for p in folder.iterdir() if p.suffix.lower() in IMG_EXTS and p.is_file()]


def split_and_copy(class_dir: Path, out_base: Path, val_ratio: float, test_ratio: float):
    images = list_images(class_dir)
    images.sort()
    random.shuffle(images)

    n = len(images)
    n_test = int(n * test_ratio)
    n_val = int(n * val_ratio)
    n_train = n - n_val - n_test

    splits = {
        "train": images[:n_train],
        "val": images[n_train:n_train + n_val],
        "test": images[n_train + n_val:]
    }

    for split, files in splits.items():
        target_dir = out_base / split / class_dir.name
        target_dir.mkdir(parents=True, exist_ok=True)
        for f in files:
            shutil.copy2(f, target_dir / f.name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', required=True, help='Directorio origen con subcarpetas por clase')
    parser.add_argument('--dst', required=True, help='Directorio destino con splits (train/val/test)')
    parser.add_argument('--val', type=float, default=0.1, help='Proporción para validación (0-1)')
    parser.add_argument('--test', type=float, default=0.1, help='Proporción para test (0-1)')
    parser.add_argument('--seed', type=int, default=42, help='Semilla aleatoria')
    args = parser.parse_args()

    random.seed(args.seed)
    src = Path(args.src)
    dst = Path(args.dst)
    dst.mkdir(parents=True, exist_ok=True)

    class_folders = [p for p in src.iterdir() if p.is_dir()]
    if not class_folders:
        raise RuntimeError("No se encontraron subcarpetas de clases en el origen.")

    for cdir in class_folders:
        split_and_copy(cdir, dst, args.val, args.test)

    print(f"✅ Dataset preparado en: {dst}")


if __name__ == '__main__':
    main()
