import pytest

from qr_code_generator.models.colour import Colour
from qr_code_generator.services.colour_service import (
    ColourValidationError,
    parse_cmyk,
    parse_hex,
    parse_rgb,
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
