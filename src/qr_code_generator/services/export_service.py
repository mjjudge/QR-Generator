"""PNG and SVG export of generated QR codes.

PNG rendering always regenerates the QR code at a scale suited to the
chosen output size, rather than resizing an already-rasterised preview, so
the exported file has genuinely crisp, integer-scaled modules (FR-011,
FR-047) at any of the offered sizes.

SVG export has no size presets -- vector output scales to any size
without pixellation (SPECIFICATION.md §10), so there is no "target
resolution" to choose. The QR modules themselves are always true vector
paths; only a central logo, if present, is embedded as a base64 PNG
`<image>` (SVG stays self-contained -- FR-050 -- but the small logo area
is necessarily raster).
"""

from __future__ import annotations

import base64
import io
from pathlib import Path

import segno
from PIL import Image

from qr_code_generator.models.qr_settings import QRSettings
from qr_code_generator.services.logo_service import (
    DEFAULT_LOGO_SIZE_RATIO,
    apply_logo,
    effective_logo_ratio_for_modules,
    fit_logo_and_panel,
)
from qr_code_generator.services.qr_service import (
    ERROR_CORRECTION_LEVEL,
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


#: Fixed scale for SVG export. Unlike PNG, this has no bearing on how
#: large the vector modules can be displayed (they scale losslessly to
#: any size); it only sets the coordinate units used in the file and, if
#: a logo is embedded, that raster's pixel density.
DEFAULT_SVG_SCALE = 20


def render_svg_for_export(
    settings: QRSettings,
    logo: Image.Image | None = None,
    logo_size_ratio: float = DEFAULT_LOGO_SIZE_RATIO,
    scale: int = DEFAULT_SVG_SCALE,
) -> str:
    """Render a QR code as a self-contained SVG document (a string).

    The QR modules are always true vector paths (FR-046), with the quiet
    zone preserved (FR-047). If a logo is present, it is embedded as a
    base64-encoded PNG `<image>` element behind a matching solid `<rect>`
    clearance panel, using the exact same placement geometry as the PNG
    path (`logo_service.fit_logo_and_panel`) so both formats look
    consistent for the same settings.
    """
    buffer = io.BytesIO()
    qr = segno.make(settings.url, error=ERROR_CORRECTION_LEVEL)
    qr.save(
        buffer,
        kind="svg",
        scale=scale,
        border=QUIET_ZONE_MODULES,
        dark=settings.foreground_colour,
        light=settings.background_colour,
    )
    svg_text = buffer.getvalue().decode("utf-8")

    if logo is None:
        return svg_text

    symbol_modules = module_count(settings.url)
    canvas_size = (symbol_modules + 2 * QUIET_ZONE_MODULES) * scale
    effective_ratio = effective_logo_ratio_for_modules(symbol_modules, logo_size_ratio)
    panel_size, panel_position, fitted_logo, logo_position = fit_logo_and_panel(
        canvas_size, effective_ratio, logo
    )

    logo_buffer = io.BytesIO()
    fitted_logo.save(logo_buffer, format="PNG")
    logo_data_uri = base64.b64encode(logo_buffer.getvalue()).decode("ascii")

    panel_element = (
        f'<rect x="{panel_position[0]}" y="{panel_position[1]}" '
        f'width="{panel_size}" height="{panel_size}" fill="{settings.background_colour}"/>'
    )
    image_element = (
        f'<image x="{logo_position[0]}" y="{logo_position[1]}" '
        f'width="{fitted_logo.width}" height="{fitted_logo.height}" '
        f'href="data:image/png;base64,{logo_data_uri}"/>'
    )
    return svg_text.replace("</svg>", panel_element + image_element + "</svg>")


def save_svg(svg_text: str, path: Path | str) -> Path:
    """Save `svg_text` as a UTF-8 encoded SVG file at `path`."""
    file_path = Path(path)
    try:
        file_path.write_text(svg_text, encoding="utf-8")
    except OSError as error:
        raise ExportError(f"Could not save '{file_path.name}': {error}") from error
    return file_path
