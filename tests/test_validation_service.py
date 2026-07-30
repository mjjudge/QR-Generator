import socket

import pytest

from qr_code_generator.services.validation_service import (
    LONG_URL_WARNING_THRESHOLD,
    URLValidationError,
    get_url_length_warning,
    validate_url,
)


def test_accepts_valid_http_url():
    assert validate_url("http://example.com") == "http://example.com"


def test_accepts_valid_https_url():
    assert validate_url("https://example.com") == "https://example.com"


def test_rejects_empty_input():
    with pytest.raises(URLValidationError):
        validate_url("")


def test_rejects_whitespace_only_input():
    with pytest.raises(URLValidationError):
        validate_url("   ")


def test_rejects_unsupported_scheme():
    with pytest.raises(URLValidationError):
        validate_url("ftp://example.com")


def test_preserves_unusual_but_valid_url_characters_exactly():
    url = "https://example.com/path?query=1&other=2#fragment%20space"
    assert validate_url(url) == url


def test_no_length_warning_at_or_below_threshold():
    url = "https://example.com/" + "a" * (LONG_URL_WARNING_THRESHOLD - len("https://example.com/"))
    assert len(url) == LONG_URL_WARNING_THRESHOLD
    assert get_url_length_warning(url) is None


def test_length_warning_above_threshold():
    url = "https://example.com/" + "a" * LONG_URL_WARNING_THRESHOLD
    assert len(url) > LONG_URL_WARNING_THRESHOLD
    assert get_url_length_warning(url) is not None


def test_validate_url_makes_no_network_calls(monkeypatch):
    def _blocked(*_args, **_kwargs):
        raise AssertionError("validate_url must not open network connections")

    monkeypatch.setattr(socket, "socket", _blocked)

    assert validate_url("https://example.com/some/path") == "https://example.com/some/path"
