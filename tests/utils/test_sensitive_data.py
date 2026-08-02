from urllib.parse import parse_qsl, urlsplit

from tests.utils.sensitive_data import sanitize_body, sanitize_url


def test_sanitize_body_redacts_json_sensitive_fields() -> None:
    raw_body = '{"email":"user@example.com","password":"secret","card":{"cardNumber":"4242","securityCode":123}}'

    sanitized_body = sanitize_body(raw_body)

    assert "secret" not in sanitized_body
    assert "4242" not in sanitized_body
    assert "user@example.com" not in sanitized_body
    assert sanitized_body.count("<redacted>") >= 3


def test_sanitize_body_redacts_form_sensitive_fields() -> None:
    raw_body = "email=user@example.com&password=secret&movieId=42"

    sanitized_body = sanitize_body(raw_body)
    fields = dict(parse_qsl(sanitized_body, keep_blank_values=True))

    assert fields["email"] == "<redacted>"
    assert fields["password"] == "<redacted>"
    assert fields["movieId"] == "42"


def test_sanitize_url_redacts_sensitive_query_fields() -> None:
    raw_url = "https://example.test/login?email=user@example.com&password=secret&page=1"

    sanitized_url = sanitize_url(raw_url)
    query = dict(parse_qsl(urlsplit(sanitized_url).query, keep_blank_values=True))

    assert query["email"] == "<redacted>"
    assert query["password"] == "<redacted>"
    assert query["page"] == "1"


def test_sanitize_body_leaves_plain_text_unchanged() -> None:
    body = "upstream service is unavailable"

    assert sanitize_body(body) == body


def test_sanitize_url_can_redact_sensitive_path() -> None:
    url = "https://example.test/confirm/raw-token?email=user@example.com&page=1"

    sanitized_url = sanitize_url(url, redact_path=True)

    assert "raw-token" not in sanitized_url
    assert "user@example.com" not in sanitized_url
    assert "page=1" in sanitized_url
