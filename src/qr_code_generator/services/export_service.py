"""PNG export of generated QR codes.

Rendering for export always regenerates the QR code at a scale suited to
the chosen output size, rather than resizing an already-rasterised
preview, so the exported file has genuinely crisp, integer-scaled modules
(FR-011, FR-047) at any of the offered sizes. SVG export is a separate
concern (BACKLOG.md QRG-013).
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from qr_code_generator.models.qr_settings import QRSettings
from qr_code_generator.services.logo_service import DEFAULT_LOGO_SIZE_RATIO, apply_logo
from qr_code_generator.services.qr_service import (
    QUIET_ZONE_MODULES,
    generate_qr_image,
    module_count,
)

#: Preset PNG export sizes offered to the user, in pixels (FR-049).
PNG_SIZE_PRESETS: dict[str, int] = {
    "Small (512 px)": 512,
    "Medium (1024 px)": 1024,
    "Large (2048 px)": 2048,
}

DEFAULT_PNG_SIZE_LABEL = "Medium (1024 px)"


class ExportError(Exception):
    """Raised when a QR code image cannot be rendered or saved for export."""


def _scale_for_target_size(symbol_modules: int, target_pixels: int) -> int:
    """The integer module scale that renders closest to `target_pixels` wide.

    QR modules must be rendered at an integer number of pixels each
    (FR-011); this picks the nearest integer scale to the requested
    target, never less than 1.
    """
    total_modules = symbol_modules + 2 * QUIET_ZONE_MODULES
    return max(round(target_pixels / total_modules), 1)


def render_png_for_export(
    settings: QRSettings,
    size_label: str,
    logo: Image.Image | None = None,
    logo_size_ratio: float = DEFAULT_LOGO_SIZE_RATIO,
) -> Image.Image:
    """Render a QR code at a scale suited to the chosen preset size, with
    the logo (if any) recomposited at that resolution.
    """
    if size_label not in PNG_SIZE_PRESETS:
        raise ExportError(f"'{size_label}' is not a recognised export size.")

    scale = _scale_for_target_size(module_count(settings.url), PNG_SIZE_PRESETS[size_label])
    image = generate_qr_image(settings, scale=scale)
    if logo is not None:
        image = apply_logo(image, logo, size_ratio=logo_size_ratio, scale=scale)
    return image


def save_png(image: Image.Image, path: Path | str) -> Path:
    """Save `image` as a PNG file at `path`.

    The QR code itself is never exported as JPEG (FR-048); overwrite
    confirmation and file choice are a UI concern, handled by the native
    save dialog before this is called.
    """
    file_path = Path(path)
    try:
        image.convert("RGB").save(file_path, format="PNG")
    except OSError as error:
        raise ExportError(f"Could not save '{file_path.name}': {error}") from error
    return file_path
