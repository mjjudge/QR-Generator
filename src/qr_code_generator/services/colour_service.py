"""Colour parsing, validation and conversion.

Colours are represented internally as sRGB (:class:`~qr_code_generator.models.colour.Colour`).
HEX, RGB and CMYK are alternative representations that all convert through
that single internal type, which is what keeps them synchronised: there is
one source of truth, not three independent fields.

CMYK conversion uses a standard, uncalibrated formula. It is only
approximate: it does not use an ICC colour profile (SPECIFICATION.md
FR-022). Palette and graphical colour-picker UI controls exist for the
foreground colour (BACKLOG.md QRG-006); background colour controls are not
yet wired up (QRG-007).
"""

from __future__ import annotations

import re

from qr_code_generator.models.colour import Colour
from qr_code_generator.models.qr_settings import (
    DEFAULT_BACKGROUND_COLOUR,
    DEFAULT_FOREGROUND_COLOUR,
)

__all__ = [
    "DEFAULT_FOREGROUND_COLOUR",
    "DEFAULT_BACKGROUND_COLOUR",
    "PALETTE",
    "ColourValidationError",
    "parse_hex",
    "parse_rgb",
    "parse_cmyk",
    "to_cmyk",
]

_HEX_PATTERN = re.compile(r"^#?[0-9A-Fa-f]{6}$")

#: A small predefined palette offered alongside the picker/HEX/RGB/CMYK
#: entry methods (SPECIFICATION.md FR-015).
PALETTE: list[Colour] = [
    Colour(0, 0, 0),
    Colour(255, 255, 255),
    Colour(200, 16, 46),
    Colour(0, 106, 78),
    Colour(0, 61, 165),
    Colour(255, 184, 28),
]


class ColourValidationError(ValueError):
    """Raised when supplied HEX, RGB or CMYK colour input is invalid."""


def parse_hex(value: str) -> Colour:
    """Parse a 6-digit HEX colour (with or without a leading ``#``)."""
    stripped = value.strip()
    if not _HEX_PATTERN.match(stripped):
        raise ColourValidationError(f"'{value}' is not a valid 6-digit HEX colour, e.g. #1A2B3C.")
    digits = stripped.lstrip("#")
    return Colour(int(digits[0:2], 16), int(digits[2:4], 16), int(digits[4:6], 16))


def parse_rgb(red: int, green: int, blue: int) -> Colour:
    """Validate and build a colour from RGB channels, each in the range 0-255."""
    try:
        return Colour(red, green, blue)
    except ValueError as error:
        raise ColourValidationError(str(error)) from error


def parse_cmyk(cyan: float, magenta: float, yellow: float, key: float) -> Colour:
    """Validate and convert CMYK percentages (each 0-100) to an sRGB colour.

    This conversion is approximate, using the standard formula below rather
    than an ICC colour profile.
    """
    for name, value in (("cyan", cyan), ("magenta", magenta), ("yellow", yellow), ("key", key)):
        if not 0 <= value <= 100:
            raise ColourValidationError(f"{name} must be between 0 and 100, got {value}.")

    c, m, y, k = cyan / 100, magenta / 100, yellow / 100, key / 100
    red = round(255 * (1 - c) * (1 - k))
    green = round(255 * (1 - m) * (1 - k))
    blue = round(255 * (1 - y) * (1 - k))
    return Colour(red, green, blue)


def to_cmyk(colour: Colour) -> tuple[float, float, float, float]:
    """Convert an sRGB colour to approximate CMYK percentages (each 0-100)."""
    r, g, b = colour.red / 255, colour.green / 255, colour.blue / 255
    k = 1 - max(r, g, b)
    if k >= 1.0:
        return (0.0, 0.0, 0.0, 100.0)
    c = (1 - r - k) / (1 - k)
    m = (1 - g - k) / (1 - k)
    y = (1 - b - k) / (1 - k)
    return (round(c * 100, 1), round(m * 100, 1), round(y * 100, 1), round(k * 100, 1))
