"""QR code image generation using Segno."""

from __future__ import annotations

import io

import segno
from PIL import Image

from qr_code_generator.models.qr_settings import QRSettings

QUIET_ZONE_MODULES = 4
ERROR_CORRECTION_LEVEL = "h"
DEFAULT_SCALE = 10


def generate_qr_image(settings: QRSettings, scale: int = DEFAULT_SCALE) -> Image.Image:
    """Render the URL in ``settings`` as a QR code image.

    Uses error-correction level H (the highest level Segno supports) so the
    generated codes remain scannable once a central logo overlay is added in
    a later task, and a conventional quiet zone of four modules.
    """
    qr = segno.make(settings.url, error=ERROR_CORRECTION_LEVEL)
    buffer = io.BytesIO()
    qr.save(
        buffer,
        kind="png",
        scale=scale,
        border=QUIET_ZONE_MODULES,
        dark=settings.foreground_colour,
        light=settings.background_colour,
    )
    buffer.seek(0)
    return Image.open(buffer).convert("RGB")
