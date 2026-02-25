import logging
from unittest.mock import Mock
from urllib.parse import parse_qsl, urlsplit

import pytest
import requests

from tests.models.response_models import ErrorResponse
from tests.request.custom_requester import CustomRequester


def test_send_request_retries_once_on_read_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    session = Mock()
    session.headers = {}

    successful_response = Mock()
    successful_response.ok = True
    successful_response.status_code = 200
    successful_response.text = "{}"
    successful_response.json.return_value = {}

    session.request.side_effect = [
        requests.exceptions.ReadTimeout("first timeout"),
        successful_response,
    ]

    monkeypatch.setattr(CustomRequester, "_attach_request_details", lambda *args, **kwargs: None)
    monkeypatch.setattr(CustomRequester, "_attach_response_details", lambda *args, **kwargs: None)
    monkeypatch.setattr(CustomRequester, "log_request_and_response", lambda *args, **kwargs: None)
    monkeypatch.setattr(CustomRequester, "SLEEP_FN", lambda *_: None)

    requester = CustomRequester(session=session, base_url="https://example.test")
    response = requester.get("/ping")

    assert response is successful_response
    assert session.request.call_count == 2


def test_parse_error_response_handles_non_json_body() -> None:
    response = Mock()
    response.status_code = 502
    response.reason = "Bad Gateway"
    response.text = "<html>upstream failed</html>"
    response.json.side_effect = ValueError("not json")

    parsed = CustomRequester.parse_error_response(response)

    assert isinstance(parsed, ErrorResponse)
    assert parsed.statusCode == 502
    assert parsed.message == "<html>upstream failed</html>"


def test_send_request_uses_injected_sleep_function(monkeypatch: pytest.MonkeyPatch) -> None:
    session = Mock()
    session.headers = {}

    successful_response = Mock()
    successful_response.ok = True
    successful_response.status_code = 200
    successful_response.text = "{}"
    successful_response.json.return_value = {}

    session.request.side_effect = [
        requests.exceptions.ReadTimeout("first timeout"),
        successful_response,
    ]

    sleep_spy = Mock()
    monkeypatch.setattr(CustomRequester, "SLEEP_FN", sleep_spy)
    monkeypatch.setattr(CustomRequester, "_attach_request_details", lambda *args, **kwargs: None)
    monkeypatch.setattr(CustomRequester, "_attach_response_details", lambda *args, **kwargs: None)
    monkeypatch.setattr(CustomRequester, "log_request_and_response", lambda *args, **kwargs: None)

    requester = CustomRequester(session=session, base_url="https://example.test")
    response = requester.get("/ping")

    assert response is successful_response
    sleep_spy.assert_called_once_with(CustomRequester.RETRY_DELAY_SECONDS)


@pytest.mark.parametrize(
    ("request_base_url", "endpoint", "expected_url"),
    [
        ("https://example.test", "ping", "https://example.test/ping"),
        ("https://example.test/", "/ping", "https://example.test/ping"),
        ("https://example.test/", "ping", "https://example.test/ping"),
    ],
)
def test_send_request_normalizes_url(
    request_base_url: str, endpoint: str, expected_url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    session = Mock()
    session.headers = {}

    successful_response = Mock()
    successful_response.ok = True
    successful_response.status_code = 200
    successful_response.text = "{}"
    successful_response.json.return_value = {}

    session.request.return_value = successful_response

    monkeypatch.setattr(CustomRequester, "_attach_request_details", lambda *args, **kwargs: None)
    monkeypatch.setattr(CustomRequester, "_attach_response_details", lambda *args, **kwargs: None)
    monkeypatch.setattr(CustomRequester, "log_request_and_response", lambda *args, **kwargs: None)

    requester = CustomRequester(session=session, base_url=request_base_url)
    requester.get(endpoint)

    assert session.request.call_args.args[1] == expected_url


def test_sanitize_request_body_redacts_json_sensitive_fields() -> None:
    raw_body = '{"email":"user@example.com","password":"secret","card":{"cardNumber":"4242","securityCode":123}}'

    sanitized = CustomRequester._sanitize_request_body(raw_body)

    assert "secret" not in sanitized
    assert "4242" not in sanitized
    assert "user@example.com" not in sanitized
    assert sanitized.count("<redacted>") >= 3


def test_sanitize_request_body_redacts_form_sensitive_fields() -> None:
    raw_body = "email=user@example.com&password=secret&movieId=42"

    sanitized = CustomRequester._sanitize_request_body(raw_body)
    pairs = dict(parse_qsl(sanitized, keep_blank_values=True))

    assert pairs["email"] == "<redacted>"
    assert pairs["password"] == "<redacted>"
    assert pairs["movieId"] == "42"


def test_sanitize_url_redacts_sensitive_query_fields() -> None:
    raw_url = "https://example.test/login?email=user@example.com&password=secret&page=1"

    sanitized = CustomRequester._sanitize_url(raw_url)
    query = dict(parse_qsl(urlsplit(sanitized).query, keep_blank_values=True))

    assert query["email"] == "<redacted>"
    assert query["password"] == "<redacted>"
    assert query["page"] == "1"


def test_parse_error_response_handles_invalid_error_schema() -> None:
    response = Mock()
    response.status_code = 500
    response.reason = "Server Error"
    response.text = '{"message": {"detail": "x"}}'
    response.json.return_value = {"message": {"detail": "x"}}

    parsed = CustomRequester.parse_error_response(response)

    assert isinstance(parsed, ErrorResponse)
    assert parsed.statusCode == 500
    assert parsed.message == '{"message": {"detail": "x"}}'


def test_parse_and_log_error_returns_error_response_and_logs(caplog: pytest.LogCaptureFixture) -> None:
    session = Mock()
    session.headers = {}
    requester = CustomRequester(session=session, base_url="https://example.test")

    response = Mock()
    response.status_code = 404
    response.reason = "Not Found"
    response.text = '{"message": "Movie not found"}'
    response.json.return_value = {"message": "Movie not found"}

    with caplog.at_level(logging.ERROR):
        error = requester.parse_and_log_error(
            response,
            domain="movie",
            action="get_by_id_failed",
            level=logging.ERROR,
            movie_id=42,
        )

    assert isinstance(error, ErrorResponse)
    assert error.statusCode == 404
    assert error.message == "Movie not found"
    assert any(
        "[MOVIE][GET_BY_ID_FAILED]" in message
        and "movie_id=42" in message
        and "status_code=404" in message
        and 'error="Movie not found"' in message
        for message in caplog.messages
    )


def test_parse_and_log_error_handles_non_json_response(caplog: pytest.LogCaptureFixture) -> None:
    session = Mock()
    session.headers = {}
    requester = CustomRequester(session=session, base_url="https://example.test")

    response = Mock()
    response.status_code = 502
    response.reason = "Bad Gateway"
    response.text = "upstream unavailable"
    response.json.side_effect = ValueError("not json")

    with caplog.at_level(logging.WARNING):
        error = requester.parse_and_log_error(
            response,
            domain="payment",
            action="create_failed",
            level=logging.WARNING,
        )

    assert isinstance(error, ErrorResponse)
    assert error.statusCode == 502
    assert error.message == "upstream unavailable"
    assert any(
        "[PAYMENT][CREATE_FAILED]" in message
        and "status_code=502" in message
        and 'error="upstream unavailable"' in message
        for message in caplog.messages
    )


def test_custom_requester_uses_subclass_name_for_logger() -> None:
    class DummyRequester(CustomRequester):
        pass

    session = Mock()
    session.headers = {}

    requester = DummyRequester(session=session, base_url="https://example.test")

    assert requester.logger.name == "DummyRequester"
