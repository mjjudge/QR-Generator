import pytest
from PIL import Image

from qr_code_generator.services.logo_service import LogoValidationError, load_logo


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
