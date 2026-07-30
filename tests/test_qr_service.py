import segno
from PIL import Image

from qr_code_generator.models.qr_settings import QRSettings
from qr_code_generator.services.qr_service import ERROR_CORRECTION_LEVEL, generate_qr_image


def test_error_correction_is_always_level_h():
    # A central logo (QRG-010) always requires level H; rather than only
    # documenting this, assert it so a future change can't silently regress
    # logo safety (FR-037).
    assert ERROR_CORRECTION_LEVEL == "h"


def test_generates_an_image_for_a_valid_url():
    image = generate_qr_image(QRSettings(url="https://example.com"))
    assert isinstance(image, Image.Image)


def test_uses_the_url_supplied_in_settings(monkeypatch):
    captured = {}
    original_make = segno.make

    def recording_make(content, **kwargs):
        captured["content"] = content
        return original_make(content, **kwargs)

    monkeypatch.setattr("qr_code_generator.services.qr_service.segno.make", recording_make)

    generate_qr_image(QRSettings(url="https://example.org/specific-path"))

    assert captured["content"] == "https://example.org/specific-path"
