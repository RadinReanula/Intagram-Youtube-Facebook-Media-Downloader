import pytest

from app.errors import ApiError
from app.security.urls import host_platform, validate_public_url


def test_accepts_supported_hosts():
    assert host_platform("www.youtube.com") == "youtube"
    assert host_platform("youtu.be") == "youtube"
    assert host_platform("m.facebook.com") == "facebook"
    assert host_platform("fb.watch") == "facebook"
    assert host_platform("www.instagram.com") == "instagram"
    assert host_platform("instagr.am") == "instagram"


def test_rejects_other_domains():
    with pytest.raises(ApiError) as caught:
        validate_public_url("https://example.com/watch?v=1")
    assert caught.value.code == "unsupported"


def test_rejects_ip_literals_and_bad_schemes():
    with pytest.raises(ApiError) as caught:
        validate_public_url("https://127.0.0.1/watch")
    assert caught.value.code == "unsupported"
    with pytest.raises(ApiError) as caught:
        validate_public_url("file:///etc/passwd")
    assert caught.value.code == "invalid_link"
    with pytest.raises(ApiError):
        validate_public_url("https://user:pass@youtube.com/watch?v=abc")


def test_trims_whitespace():
    assert validate_public_url("  https://youtu.be/abcdefghijk  ").startswith("https://")
