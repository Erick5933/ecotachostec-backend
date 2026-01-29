import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Dict, Optional, Tuple

import requests


def sanitize_label(label: str) -> str:
    """Return a filesystem-safe class label.

    Keeps letters, numbers, dash and underscore. Replaces others with underscore.
    Collapses repeats and strips edges.
    """
    label = label.strip().lower()
    # Common prefixes in OpenAI JSONL exports (multi-language)
    for prefix in (
        "class:",
        "label:",
        "category:",
        "clase:",
        "etiqueta:",
        "categoria:",
    ):
        if label.startswith(prefix):
            label = label[len(prefix) :].strip()
            break
    # Keep only safe chars
    label = re.sub(r"[^a-z0-9_-]+", "_", label)
    label = re.sub(r"_+", "_", label).strip("_-")
    return label or "unknown"


def safe_filename(name: str) -> str:
    name = re.sub(r"[^a-zA-Z0-9_.-]", "_", name)
    name = re.sub(r"_+", "_", name)
    return name or f"img_{int(time.time()*1000)}.jpg"


def ext_from_url(url: str) -> str:
    # Try to infer extension from URL, fallback to .jpg
    path = url.split("?")[0]
    ext = os.path.splitext(path)[1].lower()
    if ext in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}:
        return ext
    return ".jpg"


def parse_record(d: Dict) -> Tuple[Optional[str], Optional[str]]:
    """Extract (image_url, label) from a JSON record.

    Supports common Roboflow/OpenAI JSONL variants.
    """
    # 1) Flat keys (Roboflow/simple exports)
    url = (
        d.get("image_url")
        or d.get("image")
        or d.get("url")
        or d.get("file")
    )
    label = (
        d.get("label")
        or d.get("class")
        or d.get("class_name")
        or d.get("category")
        or d.get("caption")
    )
    if not label and isinstance(d.get("text"), str):
        label = d["text"].strip()

    # 2) OpenAI-style messages [{role, content:[{type: input_image,image_url}, {type:text|output_text,text}]}]
    if (url is None or label is None) and isinstance(d.get("messages"), list):
        try:
            msgs = d["messages"]
            # Find first image_url in any message content
            for m in msgs:
                content = m.get("content")
                if isinstance(content, list):
                    for c in content:
                        if isinstance(c, dict) and c.get("type") in {"input_image", "image"}:
                            if not url:
                                url = c.get("image_url") or c.get("url")
                        if isinstance(c, dict) and c.get("type") in {"output_text", "text"} and not label:
                            t = c.get("text")
                            if isinstance(t, str) and t.strip():
                                label = t.strip()
                                break
            # Sometimes assistant message is separated
            if label is None:
                for m in msgs:
                    if m.get("role") == "assistant":
                        content = m.get("content")
                        if isinstance(content, list):
                            for c in content:
                                if isinstance(c, dict) and c.get("type") in {"output_text", "text"}:
                                    t = c.get("text")
                                    if isinstance(t, str) and t.strip():
                                        label = t.strip()
                                        break
        except Exception:
            pass

    if isinstance(label, dict):
        # Some exports might wrap label in {"label": "..."}
        label = label.get("label") or label.get("name")

    if isinstance(label, str):
        label = sanitize_label(label)

    return url, label


def download(url: str, dst: Path, timeout: float = 15.0, retries: int = 2) -> bool:
    last_exc = None
    for _ in range(retries + 1):
        try:
            with requests.get(url, stream=True, timeout=timeout) as r:
                r.raise_for_status()
                dst.parent.mkdir(parents=True, exist_ok=True)
                with open(dst, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            return True
        except Exception as e:  # noqa: BLE001 - best-effort downloader
            last_exc = e
            time.sleep(0.5)
    print(f"WARN: failed to download {url}: {last_exc}")
    return False


def convert_split(jsonl_path: Path, out_root: Path, split_name: str, limit: Optional[int] = None) -> Tuple[int, int]:
    """Convert one JSONL file into folder-per-class structure.

    Returns (ok_count, skip_count).
    """
    ok = 0
    skip = 0
    if not jsonl_path.exists():
        print(f"INFO: {jsonl_path.name} not found, skipping split '{split_name}'.")
        return ok, skip

    with open(jsonl_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            if limit and ok >= limit:
                break
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"WARN: JSON error at line {i}: {e}")
                skip += 1
                continue

            url, label = parse_record(d)
            if not url or not label:
                skip += 1
                continue

            ext = ext_from_url(url)
            fname = safe_filename(f"{i}{ext}")
            out_path = out_root / split_name / label / fname
            if download(url, out_path):
                ok += 1
            else:
                skip += 1

    return ok, skip


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Convert Roboflow 'OpenAI GPT-4 Classification' JSONL export to "
            "folder-per-class dataset (train/val/test/<class>/image.jpg)."
        )
    )
    parser.add_argument("--src", required=True, help="Path containing _annotations.*.jsonl files")
    parser.add_argument(
        "--dst",
        default=None,
        help="Output dataset root (default: <src>/_converted_cls)",
    )
    parser.add_argument("--limit", type=int, default=None, help="Optional per-split limit for quick tests")
    args = parser.parse_args()

    src = Path(args.src)
    if not src.exists():
        print(f"ERROR: src path not found: {src}")
        return 1

    dst = Path(args.dst) if args.dst else src / "_converted_cls"
    dst.mkdir(parents=True, exist_ok=True)

    files = {
        "train": src / "_annotations.train.jsonl",
        "val": src / "_annotations.valid.jsonl",  # Roboflow uses 'valid'
        "test": src / "_annotations.test.jsonl",
    }

    total_ok = 0
    total_skip = 0
    for split, path in files.items():
        ok, skip = convert_split(path, dst, split, limit=args.limit)
        print(f"Split {split}: saved={ok}, skipped={skip}")
        total_ok += ok
        total_skip += skip

    print(f"Done. Total saved={total_ok}, skipped={total_skip}. Output: {dst}")
    if total_ok == 0:
        print(
            "NOTE: No images saved. Ensure your JSONL contains 'image_url'/'image' and a label ('label'/'class'/'text')."
        )
    return 0 if total_ok > 0 else 2


if __name__ == "__main__":
    sys.exit(main())
