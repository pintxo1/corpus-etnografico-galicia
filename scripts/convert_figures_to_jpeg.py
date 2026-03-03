#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PIL import Image


@dataclass
class FigureSources:
    png: Optional[Path] = None
    pdf: Optional[Path] = None


def discover_figures(root: Path) -> Dict[Path, FigureSources]:
    grouped: Dict[Path, FigureSources] = {}

    for file_path in root.rglob("*"):
        if not file_path.is_file():
            continue
        if not file_path.name.startswith("fig_"):
            continue

        suffix = file_path.suffix.lower()
        if suffix not in {".png", ".pdf"}:
            continue

        jpeg_path = file_path.with_suffix(".jpeg")
        if jpeg_path not in grouped:
            grouped[jpeg_path] = FigureSources()

        if suffix == ".png":
            grouped[jpeg_path].png = file_path
        elif suffix == ".pdf":
            grouped[jpeg_path].pdf = file_path

    return grouped


def png_to_jpeg(src: Path, dst: Path, quality: int = 95) -> None:
    with Image.open(src) as image:
        if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
            alpha_image = image.convert("RGBA")
            background = Image.new("RGB", alpha_image.size, (255, 255, 255))
            background.paste(alpha_image, mask=alpha_image.split()[3])
            output = background
        else:
            output = image.convert("RGB")

        output.save(dst, "JPEG", quality=quality)


def pdf_to_jpeg(src: Path, dst: Path, dpi: int = 300, quality: int = 95) -> None:
    try:
        from pdf2image import convert_from_path  # type: ignore

        pages = convert_from_path(str(src), dpi=dpi, first_page=1, last_page=1)
        if not pages:
            raise RuntimeError("pdf2image no devolvió páginas")

        page = pages[0].convert("RGB")
        page.save(dst, "JPEG", quality=quality)
        return
    except ModuleNotFoundError:
        pass

    magick = shutil.which("magick")
    convert = shutil.which("convert")

    if magick:
        cmd = [magick, "-density", str(dpi), f"{src}[0]", "-quality", str(quality), str(dst)]
    elif convert:
        cmd = [convert, "-density", str(dpi), f"{src}[0]", "-quality", str(quality), str(dst)]
    else:
        raise RuntimeError(
            "No se encontró backend para PDF. Instala uno de estos:\n"
            "  - pip install pdf2image (y poppler en sistema), o\n"
            "  - brew install imagemagick"
        )

    subprocess.run(cmd, check=True, capture_output=True, text=True)


def choose_source(sources: FigureSources) -> Tuple[Optional[Path], str]:
    if sources.png is not None:
        return sources.png, "png"
    if sources.pdf is not None:
        return sources.pdf, "pdf"
    return None, "none"


def run(root: Path) -> int:
    grouped = discover_figures(root)

    converted = 0
    omitted = 0
    errors: List[str] = []

    for jpeg_path, sources in sorted(grouped.items(), key=lambda x: str(x[0])):
        src, src_type = choose_source(sources)
        if src is None:
            omitted += 1
            continue

        if sources.png is not None and sources.pdf is not None:
            omitted += 1  # PDF omitido por prioridad de PNG

        try:
            jpeg_path.parent.mkdir(parents=True, exist_ok=True)
            if src_type == "png":
                png_to_jpeg(src, jpeg_path, quality=95)
            else:
                pdf_to_jpeg(src, jpeg_path, dpi=300, quality=95)
            converted += 1
        except Exception as exc:
            errors.append(f"{src} -> {jpeg_path}: {exc}")

    print("\n=== RESUMEN CONVERSIÓN FIGURAS -> JPEG ===")
    print(f"Raíz escaneada: {root}")
    print(f"Candidatas encontradas: {len(grouped)}")
    print(f"Convertidas: {converted}")
    print(f"Omitidas: {omitted}")
    print(f"Errores: {len(errors)}")

    if errors:
        print("\n--- LISTA DE ERRORES ---")
        for err in errors:
            print(f"- {err}")

    return 1 if errors else 0


def main() -> int:
    default_root = Path(__file__).resolve().parents[1]

    parser = argparse.ArgumentParser(
        description="Convierte figuras fig_*.png / fig_*.pdf a .jpeg (prioridad PNG; fallback PDF primera página)."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=default_root,
        help="Ruta raíz a escanear (por defecto: raíz del repo).",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    if not root.exists():
        print(f"Ruta no existe: {root}")
        return 1

    return run(root)


if __name__ == "__main__":
    sys.exit(main())
