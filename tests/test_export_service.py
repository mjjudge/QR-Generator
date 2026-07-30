import pytest
import zxingcpp
from PIL import Image

from qr_code_generator.models.qr_settings import QRSettings
from qr_code_generator.services.export_service import (
    PNG_SIZE_PRESETS,
    ExportError,
    render_png_for_export,
    save_png,
)
from qr_code_generator.services.qr_service import QUIET_ZONE_MODULES, module_count


@pytest.mark.parametrize("size_label", list(PNG_SIZE_PRESETS))
def test_render_png_for_export_is_close_to_the_requested_size(size_label):
    url = "https://example.com"
    settings = QRSettings(url=url)
    target_pixels = PNG_SIZE_PRESETS[size_label]
    total_modules = module_count(url) + 2 * QUIET_ZONE_MODULES

    image = render_png_for_export(settings, size_label)

    assert abs(image.width - target_pixels) <= total_modules
    assert image.width == image.height


def test_render_png_for_export_rejects_an_unknown_size_label():
    with pytest.raises(ExportError):
        render_png_for_export(QRSettings(url="https://example.com"), "Enormous (9999 px)")


def test_render_png_for_export_includes_the_logo_when_provided():
    settings = QRSettings(url="https://example.com")
    logo = Image.new("RGB", (100, 100), (30, 144, 255))

    with_logo = render_png_for_export(settings, "Small (512 px)", logo=logo)
    without_logo = render_png_for_export(settings, "Small (512 px)", logo=None)

    centre = (with_logo.width // 2, with_logo.height // 2)
    assert with_logo.getpixel(centre) != without_logo.getpixel(centre)


def test_save_png_writes_a_reopenable_file(tmp_path):
    image = render_png_for_export(QRSettings(url="https://example.com"), "Small (512 px)")
    path = tmp_path / "qrcode.png"

    result_path = save_png(image, path)

    assert result_path == path
    reopened = Image.open(path)
    assert reopened.format == "PNG"
    assert reopened.size == image.size


def test_exported_png_decodes_to_the_exact_url(tmp_path):
    url = "https://example.com/exported"
    image = render_png_for_export(QRSettings(url=url), "Medium (1024 px)")
    path = tmp_path / "qrcode.png"

    save_png(image, path)

    decoded = zxingcpp.read_barcodes(Image.open(path))
    assert len(decoded) == 1
    assert decoded[0].text == url


def test_save_png_raises_export_error_for_an_unwritable_path(tmp_path):
    image = render_png_for_export(QRSettings(url="https://example.com"), "Small (512 px)")
    unwritable_path = tmp_path / "no-such-directory" / "qrcode.png"

    with pytest.raises(ExportError):
        save_png(image, unwritable_path)
