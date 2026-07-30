import pytest

from qr_code_generator.models.colour import Colour
from qr_code_generator.services.colour_service import (
    ColourValidationError,
    contrast_ratio,
    get_contrast_warning,
    parse_cmyk,
    parse_hex,
    parse_rgb,
    relative_luminance,
    to_cmyk,
)


def test_parse_hex_accepts_leading_hash():
    assert parse_hex("#1A2B3C") == Colour(0x1A, 0x2B, 0x3C)


def test_parse_hex_accepts_no_leading_hash():
    assert parse_hex("1a2b3c") == Colour(0x1A, 0x2B, 0x3C)


def test_parse_hex_rejects_wrong_length():
    with pytest.raises(ColourValidationError):
        parse_hex("#1A2B3")


def test_parse_hex_rejects_non_hex_characters():
    with pytest.raises(ColourValidationError):
        parse_hex("#GGGGGG")


def test_parse_rgb_accepts_valid_channels():
    assert parse_rgb(255, 0, 128) == Colour(255, 0, 128)


def test_parse_rgb_rejects_out_of_range_channel():
    with pytest.raises(ColourValidationError):
        parse_rgb(256, 0, 0)


def test_parse_rgb_rejects_negative_channel():
    with pytest.raises(ColourValidationError):
        parse_rgb(0, -1, 0)


def test_parse_cmyk_rejects_out_of_range_component():
    with pytest.raises(ColourValidationError):
        parse_cmyk(0, 0, 0, 101)


@pytest.mark.parametrize(
    ("rgb", "cmyk"),
    [
        (Colour(0, 0, 0), (0.0, 0.0, 0.0, 100.0)),
        (Colour(255, 255, 255), (0.0, 0.0, 0.0, 0.0)),
        (Colour(255, 0, 0), (0.0, 100.0, 100.0, 0.0)),
    ],
)
def test_rgb_to_cmyk_known_values(rgb, cmyk):
    assert to_cmyk(rgb) == cmyk


@pytest.mark.parametrize(
    ("cmyk", "rgb"),
    [
        ((0, 0, 0, 100), Colour(0, 0, 0)),
        ((0, 0, 0, 0), Colour(255, 255, 255)),
        ((0, 100, 100, 0), Colour(255, 0, 0)),
    ],
)
def test_cmyk_to_rgb_known_values(cmyk, rgb):
    assert parse_cmyk(*cmyk) == rgb


def test_hex_and_rgb_stay_synchronised_via_the_same_colour():
    from_hex = parse_hex("#FF0080")
    from_rgb = parse_rgb(255, 0, 128)
    assert from_hex == from_rgb
    assert from_hex.to_hex() == "#FF0080"


def test_relative_luminance_of_black_is_zero():
    assert relative_luminance(Colour(0, 0, 0)) == pytest.approx(0.0)


def test_relative_luminance_of_white_is_one():
    assert relative_luminance(Colour(255, 255, 255)) == pytest.approx(1.0)


def test_contrast_ratio_of_black_and_white_is_maximal():
    assert contrast_ratio(Colour(0, 0, 0), Colour(255, 255, 255)) == pytest.approx(21.0)


def test_contrast_ratio_is_order_independent():
    black, white = Colour(0, 0, 0), Colour(255, 255, 255)
    assert contrast_ratio(black, white) == contrast_ratio(white, black)


def test_no_contrast_warning_for_black_on_white():
    assert get_contrast_warning(Colour(0, 0, 0), Colour(255, 255, 255)) is None


def test_contrast_warning_for_low_contrast_pair():
    warning = get_contrast_warning(Colour(220, 220, 220), Colour(255, 255, 255))
    assert warning is not None
    assert "contrast is low" in warning


def test_contrast_warning_for_light_foreground_on_dark_background():
    warning = get_contrast_warning(Colour(255, 255, 255), Colour(0, 0, 0))
    assert warning is not None
    assert "lighter than the background" in warning
    assert "contrast is low" not in warning
