"""Unit tests for trusted-host helper."""
import pytest

from app.middleware.auth import _is_trusted_host


@pytest.mark.parametrize(
    "host,expected",
    [
        (None, False),
        ("", False),
        ("127.0.0.1", True),
        ("::1", True),
        ("localhost", True),
        ("10.0.0.1", True),
        ("192.168.1.1", True),
        ("172.16.0.1", True),
        ("172.31.255.255", True),
        ("172.15.0.1", False),
        ("172.32.0.1", False),
        ("8.8.8.8", False),
    ],
)
def test_is_trusted_host(host, expected):
    assert _is_trusted_host(host) is expected
