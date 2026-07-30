"""URL validation for user-supplied QR code content.

Validation never contacts the destination URL: it only inspects the text
the user typed (see SPECIFICATION.md FR-004, NFR-001).
"""

from __future__ import annotations

_SUPPORTED_SCHEMES = ("http://", "https://")

#: Above this length, a QR code becomes noticeably denser and harder to
#: scan reliably (SPECIFICATION.md FR-006).
LONG_URL_WARNING_THRESHOLD = 300


class URLValidationError(ValueError):
    """Raised when a supplied URL is empty or does not use a supported scheme."""


def validate_url(url: str) -> str:
    """Validate that ``url`` is non-empty and starts with http:// or https://.

    Leading/trailing whitespace is trimmed; this is the only normalisation
    applied; the rest of the URL is preserved exactly as entered (FR-003).
    Raises URLValidationError if the result is empty or uses an unsupported
    scheme.
    """
    stripped = url.strip()
    if not stripped:
        raise URLValidationError("Please enter a URL.")
    if not stripped.startswith(_SUPPORTED_SCHEMES):
        raise URLValidationError("The URL must start with http:// or https://.")
    return stripped


def get_url_length_warning(url: str) -> str | None:
    """Return a warning message if ``url`` is long enough to produce a dense,
    harder-to-scan QR code, or None if its length is unremarkable.
    """
    if len(url) > LONG_URL_WARNING_THRESHOLD:
        return (
            f"This URL is {len(url)} characters long. The resulting QR code will be "
            "denser and may be harder to scan reliably, especially when printed small."
        )
    return None
