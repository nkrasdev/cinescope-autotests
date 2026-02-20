from unittest.mock import Mock

import pytest
import requests

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

    requester = CustomRequester(session=session, base_url="https://example.test")
    response = requester.get("/ping")

    assert response is successful_response
    assert session.request.call_count == 2
