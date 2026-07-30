"""Central logo file loading and validation.

This module only loads and validates a user-selected image file, returning
a safe, independent in-memory copy. Compositing a validated logo onto a QR
code is a separate concern, built on top of this (BACKLOG.md QRG-010),
once finder-pattern protection and safe sizing are designed.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, UnidentifiedImageError

#: Pillow reports both ``.jpg`` and ``.jpeg`` files as format "JPEG"; the
#: file's actual decoded content is what is checked here, never its
#: extension (SPECIFICATION.md FR-029, NFR-008).
_ACCEPTED_FORMATS = frozenset({"PNG", "JPEG"})


class LogoValidationError(ValueError):
    """Raised when a supplied logo file cannot be used as a central image."""


def load_logo(path: Path | str) -> Image.Image:
    """Load and validate an image file as a candidate central logo.

    Returns a new, fully-decoded, independent in-memory copy. The file on
    disk is only ever opened for reading; it is never modified (FR-040).
    """
    file_path = Path(path)
    try:
        with Image.open(file_path) as image:
            image.load()
            if image.format not in _ACCEPTED_FORMATS:
                raise LogoValidationError(
                    f"'{file_path.name}' is a {image.format or 'unrecognised'} file; "
                    "only PNG, JPEG and JPG images are supported."
                )
            return image.copy()
    except FileNotFoundError as error:
        raise LogoValidationError(f"'{file_path.name}' could not be found.") from error
    except UnidentifiedImageError as error:
        raise LogoValidationError(
            f"'{file_path.name}' is not a valid image file, or it is corrupt."
        ) from error
    except OSError as error:
        raise LogoValidationError(f"'{file_path.name}' could not be read: {error}") from error
