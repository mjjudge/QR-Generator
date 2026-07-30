import base64
import io
import xml.etree.ElementTree as ET

import pytest
import segno
import zxingcpp
from PIL import Image

from qr_code_generator.models.qr_settings import QRSettings
from qr_code_generator.services.export_service import (
    DEFAULT_SVG_SCALE,
    PNG_SIZE_PRESETS,
    ExportError,
    render_png_for_export,
    render_svg_for_export,
    save_png,
    save_svg,
)
from qr_code_generator.services.logo_service import (
    effective_logo_ratio_for_modules,
    fit_logo_and_panel,
)
from qr_code_generator.services.qr_service import (
    ERROR_CORRECTION_LEVEL,
    QUIET_ZONE_MODULES,
    module_count,
)

_SVG_NAMESPACE = "{http://www.w3.org/2000/svg}"


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


def test_render_svg_for_export_matches_segno_directly_when_no_logo_is_present():
    # With no logo, this must be exactly what Segno itself produces --
    # proving no unintended modification of the vector modules.
    settings = QRSettings(url="https://example.com")
    buffer = io.BytesIO()
    segno.make(settings.url, error=ERROR_CORRECTION_LEVEL).save(
        buffer,
        kind="svg",
        scale=DEFAULT_SVG_SCALE,
        border=QUIET_ZONE_MODULES,
        dark=settings.foreground_colour,
        light=settings.background_colour,
    )
    expected = buffer.getvalue().decode("utf-8")

    assert render_svg_for_export(settings) == expected


def test_render_svg_for_export_is_well_formed_xml_with_a_logo():
    logo = Image.new("RGB", (100, 100), (30, 144, 255))
    svg_text = render_svg_for_export(QRSettings(url="https://example.com"), logo=logo)

    root = ET.fromstring(svg_text)  # raises if malformed
    tags = [child.tag for child in root]

    assert f"{_SVG_NAMESPACE}g" in tags  # the untouched vector QR modules
    assert f"{_SVG_NAMESPACE}rect" in tags  # the background clearance panel
    assert f"{_SVG_NAMESPACE}image" in tags  # the embedded logo


def test_render_svg_for_export_leaves_the_qr_modules_untouched_when_a_logo_is_present():
    settings = QRSettings(url="https://example.com")
    logo = Image.new("RGB", (100, 100), (30, 144, 255))

    without_logo = render_svg_for_export(settings)
    with_logo = render_svg_for_export(settings, logo=logo)

    without_logo_group = ET.fromstring(without_logo).find(f"{_SVG_NAMESPACE}g")
    with_logo_group = ET.fromstring(with_logo).find(f"{_SVG_NAMESPACE}g")
    assert ET.tostring(with_logo_group) == ET.tostring(without_logo_group)


def test_render_svg_for_export_panel_uses_the_exact_background_colour():
    settings = QRSettings(url="https://example.com", background_colour="#123456")
    logo = Image.new("RGB", (100, 100), (30, 144, 255))

    svg_text = render_svg_for_export(settings, logo=logo)

    rect = ET.fromstring(svg_text).find(f"{_SVG_NAMESPACE}rect")
    assert rect.get("fill") == "#123456"


def test_render_svg_for_export_embeds_the_logo_at_the_expected_geometry():
    settings = QRSettings(url="https://example.com")
    logo = Image.new("RGB", (100, 100), (30, 144, 255))

    svg_text = render_svg_for_export(settings, logo=logo)

    symbol_modules = module_count(settings.url)
    canvas_size = (symbol_modules + 2 * QUIET_ZONE_MODULES) * DEFAULT_SVG_SCALE
    effective_ratio = effective_logo_ratio_for_modules(symbol_modules, 0.18)
    expected_panel_size, expected_panel_position, expected_fitted_logo, expected_logo_position = (
        fit_logo_and_panel(canvas_size, effective_ratio, logo)
    )

    image_element = ET.fromstring(svg_text).find(f"{_SVG_NAMESPACE}image")
    assert int(image_element.get("width")) == expected_fitted_logo.width
    assert int(image_element.get("height")) == expected_fitted_logo.height
    assert int(image_element.get("x")) == expected_logo_position[0]
    assert int(image_element.get("y")) == expected_logo_position[1]

    embedded_bytes = base64.b64decode(image_element.get("href").split(",", 1)[1])
    embedded_logo = Image.open(io.BytesIO(embedded_bytes))
    assert embedded_logo.size == expected_fitted_logo.size
    assert expected_panel_size > 0
    assert expected_panel_position[0] >= 0


def test_save_svg_writes_the_exact_text(tmp_path):
    svg_text = render_svg_for_export(QRSettings(url="https://example.com"))
    path = tmp_path / "qrcode.svg"

    result_path = save_svg(svg_text, path)

    assert result_path == path
    assert path.read_text(encoding="utf-8") == svg_text


def test_save_svg_raises_export_error_for_an_unwritable_path(tmp_path):
    svg_text = render_svg_for_export(QRSettings(url="https://example.com"))
    unwritable_path = tmp_path / "no-such-directory" / "qrcode.svg"

    with pytest.raises(ExportError):
        save_svg(svg_text, unwritable_path)
