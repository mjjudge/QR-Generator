"""Central logo file loading, validation and placement.

Loading (`load_logo`) and placement (`apply_logo`) are kept as separate
functions with a plain `PIL.Image.Image` passed between them, so either can
be tested and reasoned about independently.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError

from qr_code_generator.services.qr_service import DEFAULT_SCALE, QUIET_ZONE_MODULES

#: Pillow reports both ``.jpg`` and ``.jpeg`` files as format "JPEG"; the
#: file's actual decoded content is what is checked here, never its
#: extension (SPECIFICATION.md FR-029, NFR-008).
_ACCEPTED_FORMATS = frozenset({"PNG", "JPEG"})

#: The three QR finder patterns are always exactly 7x7 modules, in the
#: three corners of the symbol, for every QR version (ISO/IEC 18004) --
#: this is what makes a size cap based on this constant valid regardless
#: of how large the generated QR code is.
_FINDER_PATTERN_MODULES = 7

#: Default logo footprint, as a fraction of the QR image's width (FR-035).
DEFAULT_LOGO_SIZE_RATIO = 0.18

#: Absolute maximum footprint, as a fraction of the QR image's width,
#: regardless of how much finder-pattern clearance is geometrically
#: available (FR-036). Kept well under error-correction level H's ~30%
#: correctable-codeword budget: high error correction does not make every
#: image size safe to scan (FR-038).
MAX_LOGO_SIZE_RATIO = 0.30

#: Inner margin between the clearance panel's edge and the logo itself, as
#: a fraction of the panel's size (FR-033).
_PANEL_PADDING_FRACTION = 0.12


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


def _module_count(qr_image: Image.Image, scale: int) -> int:
    """Recover the QR symbol's module count (excluding the quiet zone) from
    the rendered image's pixel width, given the scale it was rendered at.
    """
    total_modules = qr_image.width // scale
    return total_modules - 2 * QUIET_ZONE_MODULES


def max_safe_logo_ratio(qr_image: Image.Image, scale: int = DEFAULT_SCALE) -> float:
    """The largest centred, square footprint (as a fraction of image width)
    that is geometrically guaranteed not to overlap any finder pattern of
    this specific QR code.

    The three finder patterns sit only in the three corners, each
    `_FINDER_PATTERN_MODULES` (7) modules square. A centred square
    footprint of ``S`` modules avoids all three exactly when
    ``S <= module_count - 2 * _FINDER_PATTERN_MODULES + 1`` (one module of
    margin included); see BACKLOG.md QRG-010 for the full derivation. This
    holds for every QR version, since finder patterns are always 7x7
    modules regardless of symbol size -- only the safe fraction changes.
    """
    module_count = _module_count(qr_image, scale)
    total_modules = module_count + 2 * QUIET_ZONE_MODULES
    safe_span_modules = max(module_count - 2 * _FINDER_PATTERN_MODULES + 1, 0)
    return safe_span_modules / total_modules


def apply_logo(
    qr_image: Image.Image,
    logo: Image.Image,
    *,
    size_ratio: float = DEFAULT_LOGO_SIZE_RATIO,
    scale: int = DEFAULT_SCALE,
) -> Image.Image:
    """Composite `logo`, centred, onto `qr_image`, behind a matching
    background clearance panel.

    The logo's aspect ratio is always preserved -- it is never stretched
    or distorted (FR-030, FR-039). Its footprint is capped by whichever is
    smallest of: the requested `size_ratio`, `MAX_LOGO_SIZE_RATIO`, and
    `max_safe_logo_ratio` for this specific QR code (FR-034, FR-036).
    Neither `qr_image` nor `logo` is modified; a new image is returned
    (FR-040).
    """
    effective_ratio = min(size_ratio, MAX_LOGO_SIZE_RATIO, max_safe_logo_ratio(qr_image, scale))
    panel_size = round(qr_image.width * effective_ratio)
    logo_box_size = max(round(panel_size * (1 - 2 * _PANEL_PADDING_FRACTION)), 1)

    fitted_logo = ImageOps.contain(logo.convert("RGBA"), (logo_box_size, logo_box_size))

    result = qr_image.convert("RGB").copy()
    background_colour = result.getpixel((0, 0))
    panel = Image.new("RGB", (panel_size, panel_size), background_colour)

    panel_position = ((result.width - panel_size) // 2, (result.height - panel_size) // 2)
    result.paste(panel, panel_position)

    logo_position = (
        (result.width - fitted_logo.width) // 2,
        (result.height - fitted_logo.height) // 2,
    )
    result.paste(fitted_logo, logo_position, mask=fitted_logo)

    return result
