#!/usr/bin/env python3
from __future__ import annotations

from io import BytesIO
from pathlib import Path

from PIL import Image


def _convert_png_to_jpeg(png_path: Path, jpeg_path: Path, quality: int = 95) -> None:
    with Image.open(png_path) as image:
        if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
            rgba = image.convert("RGBA")
            background = Image.new("RGB", rgba.size, (255, 255, 255))
            background.paste(rgba, mask=rgba.split()[3])
            output = background
        else:
            output = image.convert("RGB")

        output.save(jpeg_path, "JPEG", quality=quality)


def _save_jpeg_from_figure(fig, jpeg_path: Path, dpi: int = 300, quality: int = 95, bbox_inches: str = "tight") -> None:
    buffer = BytesIO()
    fig.savefig(buffer, format="png", dpi=dpi, bbox_inches=bbox_inches)
    buffer.seek(0)
    with Image.open(buffer) as image:
        if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
            rgba = image.convert("RGBA")
            background = Image.new("RGB", rgba.size, (255, 255, 255))
            background.paste(rgba, mask=rgba.split()[3])
            output = background
        else:
            output = image.convert("RGB")
        output.save(jpeg_path, "JPEG", quality=quality)


def save_figure_variants(
    fig,
    base_path: Path,
    dpi: int = 300,
    save_png: bool = True,
    save_pdf: bool = True,
    save_jpeg: bool = True,
    jpeg_quality: int = 95,
    bbox_inches: str = "tight",
) -> None:
    base_path = Path(base_path)
    base_path.parent.mkdir(parents=True, exist_ok=True)

    png_path = base_path.with_suffix(".png")
    pdf_path = base_path.with_suffix(".pdf")
    jpeg_path = base_path.with_suffix(".jpeg")

    if save_png:
        fig.savefig(png_path, dpi=dpi, bbox_inches=bbox_inches)
        print(f"✅ {png_path}")

    if save_pdf:
        fig.savefig(pdf_path, format="pdf", bbox_inches=bbox_inches)
        print(f"✅ {pdf_path}")

    if save_jpeg:
        if save_png and png_path.exists():
            _convert_png_to_jpeg(png_path, jpeg_path, quality=jpeg_quality)
        else:
            _save_jpeg_from_figure(fig, jpeg_path, dpi=dpi, quality=jpeg_quality, bbox_inches=bbox_inches)
        print(f"✅ {jpeg_path}")
