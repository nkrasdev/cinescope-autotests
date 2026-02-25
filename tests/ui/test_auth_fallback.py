import pytest

from tests.ui.auth_fallback import is_dev_auth_form_fallback_url


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://cinema.local/login?email=user@example.com&password=secret", True),
        ("https://cinema.local/register?email=user@example.com", True),
        ("https://cinema.local/register?password=secret", True),
        ("https://cinema.local/login", False),
        ("https://cinema.local/payment?email=user@example.com", False),
    ],
)
def test_is_dev_auth_form_fallback_url(url: str, expected: bool) -> None:
    assert is_dev_auth_form_fallback_url(url) is expected
