import logging
from unittest.mock import Mock
from uuid import uuid4

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
    assert parsed.status_code == 502
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


def test_send_request_does_not_retry_non_idempotent_method(monkeypatch: pytest.MonkeyPatch) -> None:
    session = Mock()
    session.headers = {}
    session.request.side_effect = requests.exceptions.ReadTimeout("request outcome is unknown")

    sleep_spy = Mock()
    monkeypatch.setattr(CustomRequester, "SLEEP_FN", sleep_spy)
    monkeypatch.setattr(CustomRequester, "_attach_request_details", lambda *args, **kwargs: None)

    requester = CustomRequester(session=session, base_url="https://example.test")

    with pytest.raises(requests.exceptions.ReadTimeout):
        requester.post("/payments", json={"amount": 1})

    session.request.assert_called_once()
    sleep_spy.assert_not_called()


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


def test_request_allure_attachments_redact_sensitive_values(monkeypatch: pytest.MonkeyPatch) -> None:
    session = Mock()
    session.headers = {}
    requester = CustomRequester(session=session, base_url="https://example.test")
    attachment_bodies: list[str] = []
    password = uuid4().hex

    monkeypatch.setattr(
        "tests.request.custom_requester.allure.attach",
        lambda body, **_: attachment_bodies.append(body),
    )

    requester._attach_request_details(
        "POST",
        "https://example.test/login?email=%3Credacted%3E",
        {"email": "user@example.com", "page": 1},
        None,
        {"email": "user@example.com", "password": password, "card": {"cardNumber": "4242"}},
    )

    attachments = "\n".join(attachment_bodies)
    assert "user@example.com" not in attachments
    assert password not in attachments
    assert "4242" not in attachments
    assert "<redacted>" in attachments


def test_response_allure_attachment_redacts_sensitive_values(monkeypatch: pytest.MonkeyPatch) -> None:
    session = Mock()
    session.headers = {}
    requester = CustomRequester(session=session, base_url="https://example.test")
    response = Mock()
    response.status_code = 200
    response.json.return_value = {
        "accessToken": "raw-token",
        "user": {"email": "user@example.com", "id": "user-id"},
    }
    attachment_bodies: list[str] = []

    monkeypatch.setattr(
        "tests.request.custom_requester.allure.attach",
        lambda body, **_: attachment_bodies.append(body),
    )

    requester._attach_response_details(response)

    attachments = "\n".join(attachment_bodies)
    assert "raw-token" not in attachments
    assert "user@example.com" not in attachments
    assert "user-id" in attachments


def test_status_validation_does_not_expose_sensitive_response_values() -> None:
    session = Mock()
    session.headers = {}
    requester = CustomRequester(session=session, base_url="https://example.test")
    response = Mock(status_code=500, text='{"password":"server-echoed-secret"}')

    with pytest.raises(AssertionError) as error:
        requester._assert_expected_status(response, expected_status=200)

    assert "server-echoed-secret" not in str(error.value)
    assert "<redacted>" in str(error.value)


def test_parse_error_response_handles_invalid_error_schema() -> None:
    response = Mock()
    response.status_code = 500
    response.reason = "Server Error"
    response.text = '{"message": {"detail": "x"}}'
    response.json.return_value = {"message": {"detail": "x"}}

    parsed = CustomRequester.parse_error_response(response)

    assert isinstance(parsed, ErrorResponse)
    assert parsed.status_code == 500
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
    assert error.status_code == 404
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
    assert error.status_code == 502
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
