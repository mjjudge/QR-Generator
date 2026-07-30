import pytest
import zxingcpp
from PIL import Image

from qr_code_generator.models.qr_settings import QRSettings
from qr_code_generator.services.logo_service import (
    LogoValidationError,
    apply_logo,
    load_logo,
    max_safe_logo_ratio,
)
from qr_code_generator.services.qr_service import QUIET_ZONE_MODULES, generate_qr_image


def _write_png(path, size=(32, 32), colour=(255, 0, 0)):
    Image.new("RGB", size, colour).save(path, format="PNG")


def _write_jpeg(path, size=(32, 32), colour=(0, 255, 0)):
    Image.new("RGB", size, colour).save(path, format="JPEG")


def test_loads_a_valid_png(tmp_path):
    path = tmp_path / "logo.png"
    _write_png(path)
    image = load_logo(path)
    assert image.size == (32, 32)


@pytest.mark.parametrize("suffix", ["jpg", "jpeg"])
def test_loads_a_valid_jpeg_regardless_of_extension_spelling(tmp_path, suffix):
    path = tmp_path / f"logo.{suffix}"
    _write_jpeg(path)
    image = load_logo(path)
    assert image.size == (32, 32)


def test_rejects_missing_file(tmp_path):
    with pytest.raises(LogoValidationError):
        load_logo(tmp_path / "does-not-exist.png")


def test_rejects_corrupt_file_content(tmp_path):
    path = tmp_path / "corrupt.png"
    path.write_bytes(b"this is not an image")
    with pytest.raises(LogoValidationError):
        load_logo(path)


def test_rejects_unsupported_format_even_with_a_png_extension(tmp_path):
    # A genuine BMP saved with a misleading .png extension: validation must
    # be content-based (NFR-008), not trust the file extension.
    path = tmp_path / "disguised.png"
    Image.new("RGB", (16, 16)).save(path, format="BMP")
    with pytest.raises(LogoValidationError):
        load_logo(path)


def test_does_not_modify_the_source_file(tmp_path):
    path = tmp_path / "logo.png"
    _write_png(path)
    original_bytes = path.read_bytes()

    load_logo(path)

    assert path.read_bytes() == original_bytes


def test_returns_an_independent_in_memory_copy(tmp_path):
    path = tmp_path / "logo.png"
    _write_png(path)

    image = load_logo(path)
    path.unlink()  # if this were a lazy handle to the file, using it would now fail
    image.load()

    assert image.size == (32, 32)


def _finder_pattern_pixel_positions(
    qr_image: Image.Image, scale: int = 10
) -> list[tuple[int, int]]:
    """A pixel well inside the dark centre of each of the three finder
    patterns, in image coordinates."""
    border = QUIET_ZONE_MODULES
    inset = (border + 3) * scale  # module 3 of the 7x7 pattern: its dark centre
    right = qr_image.width - inset - 1
    bottom = qr_image.height - inset - 1
    return [(inset, inset), (right, inset), (inset, bottom)]


def test_max_safe_logo_ratio_matches_known_derivation():
    # A synthetic version-1-sized image: (21 modules + 2*4 border) * scale 10.
    image = Image.new("RGB", (290, 290), "white")
    ratio = max_safe_logo_ratio(image, scale=10)
    # Safe span = 21 - 2*7 + 1 = 8 modules, out of 29 total modules.
    assert ratio == pytest.approx(8 / 29)


def test_apply_logo_preserves_overall_image_size():
    qr_image = generate_qr_image(QRSettings(url="https://example.com"))
    wide_logo = Image.new("RGB", (200, 50), (10, 20, 30))

    result = apply_logo(qr_image, wide_logo)

    assert result.size == qr_image.size


def test_apply_logo_does_not_touch_finder_pattern_pixels():
    qr_image = generate_qr_image(QRSettings(url="https://example.com"))
    logo = Image.new("RGB", (100, 100), (255, 0, 255))

    result = apply_logo(qr_image, logo)

    for position in _finder_pattern_pixel_positions(qr_image):
        assert result.getpixel(position) == qr_image.getpixel(position)


def test_apply_logo_does_not_modify_its_inputs():
    qr_image = generate_qr_image(QRSettings(url="https://example.com"))
    logo = Image.new("RGB", (64, 64), (255, 0, 255))
    qr_bytes_before = qr_image.tobytes()
    logo_bytes_before = logo.tobytes()

    apply_logo(qr_image, logo)

    assert qr_image.tobytes() == qr_bytes_before
    assert logo.tobytes() == logo_bytes_before


@pytest.mark.parametrize(
    "url",
    [
        "http://a.co",  # about as short as validation allows: the tightest, smallest QR code
        "https://example.com/a/reasonably/typical/path?with=query&and=params",
    ],
)
def test_logo_bearing_qr_code_still_decodes_to_the_exact_url(url):
    qr_image = generate_qr_image(QRSettings(url=url))
    logo = Image.new("RGB", (80, 80), (30, 144, 255))

    result = apply_logo(qr_image, logo)

    decoded = zxingcpp.read_barcodes(result)
    assert len(decoded) == 1
    assert decoded[0].text == url
