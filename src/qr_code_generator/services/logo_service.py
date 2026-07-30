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

#: At or above this footprint, warn that a large logo can reduce scan
#: reliability even though it remains within the hard limits above
#: (FR-038). Set at 80% of `MAX_LOGO_SIZE_RATIO`.
LARGE_LOGO_WARNING_RATIO = 0.8 * MAX_LOGO_SIZE_RATIO


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
    except Image.DecompressionBombError as error:
        # Pillow's own safety limit (Image.MAX_IMAGE_PIXELS) against images
        # so large they risk exhausting memory -- this does not inherit
        # from OSError, so it needs its own clause.
        raise LogoValidationError(f"'{file_path.name}' is too large to process safely.") from error
    except OSError as error:
        raise LogoValidationError(f"'{file_path.name}' could not be read: {error}") from error


def _module_count(qr_image: Image.Image, scale: int) -> int:
    """Recover the QR symbol's module count (excluding the quiet zone) from
    the rendered image's pixel width, given the scale it was rendered at.
    """
    total_modules = qr_image.width // scale
    return total_modules - 2 * QUIET_ZONE_MODULES


def max_safe_logo_ratio_for_modules(symbol_modules: int, border: int = QUIET_ZONE_MODULES) -> float:
    """The largest centred, square footprint (as a fraction of image width)
    that is geometrically guaranteed not to overlap any finder pattern, for
    a QR symbol of `symbol_modules` modules per side.

    The three finder patterns sit only in the three corners, each
    `_FINDER_PATTERN_MODULES` (7) modules square. A centred square
    footprint of ``S`` modules avoids all three exactly when
    ``S <= symbol_modules - 2 * _FINDER_PATTERN_MODULES + 1`` (one module
    of margin included); see BACKLOG.md QRG-010 for the full derivation.
    This holds for every QR version, since finder patterns are always 7x7
    modules regardless of symbol size -- only the safe fraction changes.

    Takes a plain module count rather than a rendered image so it can be
    shared by both the PNG (`apply_logo`) and SVG (`export_service`) paths
    without either needing to rasterise anything first.
    """
    total_modules = symbol_modules + 2 * border
    safe_span_modules = max(symbol_modules - 2 * _FINDER_PATTERN_MODULES + 1, 0)
    return safe_span_modules / total_modules


def max_safe_logo_ratio(qr_image: Image.Image, scale: int = DEFAULT_SCALE) -> float:
    """`max_safe_logo_ratio_for_modules`, for an already-rendered `qr_image`."""
    return max_safe_logo_ratio_for_modules(_module_count(qr_image, scale))


def effective_logo_ratio_for_modules(symbol_modules: int, requested_ratio: float) -> float:
    """The footprint ratio actually used for a symbol of `symbol_modules`
    modules per side, after applying the absolute maximum and the
    finder-pattern-safe maximum -- whichever of the three is smallest
    (FR-034, FR-036).
    """
    return min(
        requested_ratio, MAX_LOGO_SIZE_RATIO, max_safe_logo_ratio_for_modules(symbol_modules)
    )


def effective_logo_ratio(
    qr_image: Image.Image, requested_ratio: float, scale: int = DEFAULT_SCALE
) -> float:
    """`effective_logo_ratio_for_modules`, for an already-rendered `qr_image`."""
    return effective_logo_ratio_for_modules(_module_count(qr_image, scale), requested_ratio)


def get_logo_size_warning(effective_ratio: float, requested_ratio: float) -> str | None:
    """Return a warning about the logo's size, or None if it looks safe.

    Two independent conditions are checked: whether the requested size had
    to be reduced to respect the safe/absolute limits (in which case that
    takes priority), and -- only if no reduction was needed -- whether the
    resulting size is large enough that high error correction alone may
    not guarantee reliable scanning (FR-038), even though it is
    geometrically clear of the finder patterns.
    """
    if effective_ratio < requested_ratio - 1e-9:
        return (
            f"Logo size reduced to {effective_ratio * 100:.0f}% (from the requested "
            f"{requested_ratio * 100:.0f}%) to stay clear of this QR code's finder patterns."
        )
    if effective_ratio >= LARGE_LOGO_WARNING_RATIO:
        return (
            "A logo this large can reduce scan reliability, even with high error "
            "correction; consider a smaller size, especially for printed use."
        )
    return None


def fit_logo_and_panel(
    canvas_size: int, effective_ratio: float, logo: Image.Image
) -> tuple[int, tuple[int, int], Image.Image, tuple[int, int]]:
    """Shared placement geometry for a `canvas_size`-square QR image,
    reused identically by the PNG (`apply_logo`) and SVG
    (`export_service.render_svg_for_export`) export paths so both produce
    visually consistent results for the same settings.

    Returns ``(panel_size, panel_position, fitted_logo, logo_position)``,
    all in the same pixel/unit space as `canvas_size`.
    """
    panel_size = round(canvas_size * effective_ratio)
    logo_box_size = max(round(panel_size * (1 - 2 * _PANEL_PADDING_FRACTION)), 1)
    fitted_logo = ImageOps.contain(logo.convert("RGBA"), (logo_box_size, logo_box_size))
    panel_position = ((canvas_size - panel_size) // 2, (canvas_size - panel_size) // 2)
    logo_position = (
        (canvas_size - fitted_logo.width) // 2,
        (canvas_size - fitted_logo.height) // 2,
    )
    return panel_size, panel_position, fitted_logo, logo_position


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
    or distorted (FR-030, FR-039). Its footprint is capped by
    `effective_logo_ratio`. Neither `qr_image` nor `logo` is modified; a
    new image is returned (FR-040).
    """
    effective_ratio = effective_logo_ratio(qr_image, size_ratio, scale)
    panel_size, panel_position, fitted_logo, logo_position = fit_logo_and_panel(
        qr_image.width, effective_ratio, logo
    )

    result = qr_image.convert("RGB").copy()
    background_colour = result.getpixel((0, 0))
    panel = Image.new("RGB", (panel_size, panel_size), background_colour)
    result.paste(panel, panel_position)
    result.paste(fitted_logo, logo_position, mask=fitted_logo)

    return result
