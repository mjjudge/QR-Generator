"""Typed data passed between the UI and the QR generation services."""

from __future__ import annotations

from dataclasses import dataclass

DEFAULT_FOREGROUND_COLOUR = "#000000"
DEFAULT_BACKGROUND_COLOUR = "#FFFFFF"


@dataclass(frozen=True)
class QRSettings:
    """Parameters required to generate a single QR code.

    Colour fields default to a conventional black-on-white code; palette,
    colour-picker and CMYK/HEX selection will populate them in a later task.
    """

    url: str
    foreground_colour: str = DEFAULT_FOREGROUND_COLOUR
    background_colour: str = DEFAULT_BACKGROUND_COLOUR
