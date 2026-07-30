import segno
import zxingcpp
from PIL import Image

from qr_code_generator.models.qr_settings import QRSettings
from qr_code_generator.services.qr_service import (
    ERROR_CORRECTION_LEVEL,
    QUIET_ZONE_MODULES,
    generate_qr_image,
    module_count,
)


def test_error_correction_is_always_level_h():
    # A central logo (QRG-010) always requires level H; rather than only
    # documenting this, assert it so a future change can't silently regress
    # logo safety (FR-037).
    assert ERROR_CORRECTION_LEVEL == "h"


def test_generates_an_image_for_a_valid_url():
    image = generate_qr_image(QRSettings(url="https://example.com"))
    assert isinstance(image, Image.Image)


def test_module_count_matches_the_rendered_image():
    url = "https://example.com"
    image = generate_qr_image(QRSettings(url=url), scale=1)
    # At scale=1 with the standard border, image width = module_count + 2*border.
    assert module_count(url) == image.width - 2 * QUIET_ZONE_MODULES


def test_generated_qr_decodes_to_the_exact_url_black_on_white():
    # QRG-015: the plain, no-logo, default-colour case -- decoding
    # coverage for logo-bearing codes already exists (QRG-010); this adds
    # the equivalent for the basic case, for completeness/symmetry.
    url = "https://example.com/plain"
    image = generate_qr_image(QRSettings(url=url))

    decoded = zxingcpp.read_barcodes(image)

    assert len(decoded) == 1
    assert decoded[0].text == url


def test_generated_qr_decodes_to_the_exact_url_with_custom_colours():
    url = "https://example.com/coloured"
    image = generate_qr_image(
        QRSettings(url=url, foreground_colour="#006400", background_colour="#FFFFFF")
    )

    decoded = zxingcpp.read_barcodes(image)

    assert len(decoded) == 1
    assert decoded[0].text == url


def test_uses_the_url_supplied_in_settings(monkeypatch):
    captured = {}
    original_make = segno.make

    def recording_make(content, **kwargs):
        captured["content"] = content
        return original_make(content, **kwargs)

    monkeypatch.setattr("qr_code_generator.services.qr_service.segno.make", recording_make)

    generate_qr_image(QRSettings(url="https://example.org/specific-path"))

    assert captured["content"] == "https://example.org/specific-path"
