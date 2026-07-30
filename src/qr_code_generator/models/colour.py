"""A colour represented internally as sRGB.

HEX, RGB and CMYK are alternative entry/exit representations of the same
underlying colour; converting each of them through this single type is what
keeps them synchronised (SPECIFICATION.md FR-020, FR-021).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Colour:
    """An sRGB colour with 8-bit channels."""

    red: int
    green: int
    blue: int

    def __post_init__(self) -> None:
        for name, value in (("red", self.red), ("green", self.green), ("blue", self.blue)):
            if not 0 <= value <= 255:
                raise ValueError(f"{name} must be between 0 and 255, got {value}.")

    def to_hex(self) -> str:
        """Return the colour as an uppercase 6-digit HEX string, e.g. ``#1A2B3C``."""
        return f"#{self.red:02X}{self.green:02X}{self.blue:02X}"
