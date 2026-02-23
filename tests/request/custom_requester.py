import contextlib
import json
import logging
import os
import time
from typing import Any

import allure
import requests

from tests.utils.logging_utils import log_event


class CustomRequester:
    base_headers = {"Content-Type": "application/json", "Accept": "application/json"}
    RETRYABLE_EXCEPTIONS = (requests.exceptions.Timeout, requests.exceptions.ConnectionError)
    MAX_REQUEST_ATTEMPTS = 2
    RETRY_DELAY_SECONDS = 1.0

    def __init__(self, session: requests.Session, base_url: str):
        self.session = session
        self.base_url = base_url
        self.session.headers.update(self.base_headers)
        self.logger = logging.getLogger(__name__)

    def _send_request(
        self,
        method: str,
        endpoint: str,
        params: dict | None = None,
        data: Any = None,
        json_data: Any = None,
        **kwargs,
    ) -> requests.Response:
        url = f"{self.base_url}{endpoint}"

        expected_status = kwargs.pop("expected_status", None)

        request_kwargs = kwargs
        request_kwargs.setdefault("timeout", 30)
        if params is not None:
            request_kwargs["params"] = params
        if data is not None:
            request_kwargs["data"] = data
        if json_data is not None:
            request_kwargs["json"] = json_data

        step_name = f"Выполнение {method.upper()} запроса на {url}"
        with allure.step(step_name):
            self._attach_request_details(method, url, params, data, json_data)

            response = None
            for attempt in range(1, self.MAX_REQUEST_ATTEMPTS + 1):
                try:
                    response = self.session.request(method, url, **request_kwargs)
                    break
                except self.RETRYABLE_EXCEPTIONS as exc:
                    if attempt == self.MAX_REQUEST_ATTEMPTS:
                        raise
                    log_event(
                        self.logger,
                        "http",
                        "retry",
                        level=logging.WARNING,
                        method=method.upper(),
                        url=url,
                        error_type=type(exc).__name__,
                        attempt=attempt + 1,
                        max_attempts=self.MAX_REQUEST_ATTEMPTS,
                        delay_sec=self.RETRY_DELAY_SECONDS,
                    )
                    time.sleep(self.RETRY_DELAY_SECONDS)

            if response is None:
                raise RuntimeError(f"Не удалось выполнить запрос {method.upper()} {url}")
            self._attach_response_details(response)
            self.log_request_and_response(response)
            self._validate_status_code(response, expected_status)

            return response

    def get(self, endpoint: str, params: dict | None = None, **kwargs) -> requests.Response:
        return self._send_request("GET", endpoint, params=params, **kwargs)

    def post(self, endpoint: str, data: Any = None, json: Any = None, **kwargs) -> requests.Response:
        return self._send_request("POST", endpoint, data=data, json_data=json, **kwargs)

    def patch(self, endpoint: str, data: Any = None, json: Any = None, **kwargs) -> requests.Response:
        return self._send_request("PATCH", endpoint, data=data, json_data=json, **kwargs)

    def put(self, endpoint: str, data: Any = None, json: Any = None, **kwargs) -> requests.Response:
        return self._send_request("PUT", endpoint, data=data, json_data=json, **kwargs)

    def delete(self, endpoint: str, data: Any = None, json: Any = None, **kwargs) -> requests.Response:
        return self._send_request("DELETE", endpoint, data=data, json_data=json, **kwargs)

    def _update_session_headers(self, **kwargs):
        self.session.headers.update(kwargs)

    def _validate_status_code(self, response: requests.Response, expected_status: int | None):
        if expected_status:
            assert response.status_code == expected_status, (
                f"Ожидался статус-код {expected_status}, но получен {response.status_code}. "
                f"Тело ответа: {response.text}"
            )

    def _attach_request_details(self, method, url, params, data, json_data):
        allure.attach(
            body=f"{method.upper()} {url}",
            name="Request Line",
            attachment_type=allure.attachment_type.TEXT,
        )
        if params is not None:
            allure.attach(
                body=json.dumps(params, indent=4, ensure_ascii=False),
                name="Query Parameters",
                attachment_type=allure.attachment_type.JSON,
            )
        if json_data is not None:
            allure.attach(
                body=json.dumps(json_data, indent=4, ensure_ascii=False),
                name="Request Body (JSON)",
                attachment_type=allure.attachment_type.JSON,
            )
        if data is not None:
            allure.attach(
                body=str(data),
                name="Request Body (Data)",
                attachment_type=allure.attachment_type.TEXT,
            )

    def _attach_response_details(self, response):
        status_code = response.status_code
        allure.attach(
            body=str(status_code),
            name="Response Status Code",
            attachment_type=allure.attachment_type.TEXT,
        )
        try:
            response_body = json.dumps(response.json(), indent=4, ensure_ascii=False)
            attachment_type = allure.attachment_type.JSON
        except (json.JSONDecodeError, AttributeError):
            response_body = response.text
            attachment_type = allure.attachment_type.TEXT

        allure.attach(body=response_body, name="Response Body", attachment_type=attachment_type)

    @staticmethod
    def _truncate_payload(payload: str, max_length: int = 4000) -> str:
        if len(payload) <= max_length:
            return payload
        return f"{payload[:max_length]}... <truncated {len(payload) - max_length} chars>"

    def log_request_and_response(self, response):
        try:
            request = response.request
            headers_list: list[str] = []
            for header, value in request.headers.items():
                display_value = value
                if header.lower() == "authorization":
                    display_value = "Bearer <redacted>"
                headers_list.append(f"-H '{header}: {display_value}'")
            headers_str = " \\\n".join(headers_list)
            full_test_name = f"pytest {os.environ.get('PYTEST_CURRENT_TEST', '').replace(' (call)', '')}"

            body = ""
            if hasattr(request, "body") and request.body is not None:
                body = request.body.decode("utf-8") if isinstance(request.body, bytes) else str(request.body)
                body = f"-d '{body}' \n" if body != "{}" and body else ""

            log_event(
                self.logger,
                "http",
                "request",
                method=request.method,
                url=request.url,
                test=full_test_name,
            )
            self.logger.info(
                "curl -X %s '%s' \\\n%s \\\n%s",
                request.method,
                request.url,
                headers_str,
                body,
            )

            response_data = response.text
            with contextlib.suppress(json.JSONDecodeError):
                response_data = json.dumps(json.loads(response.text), indent=4, ensure_ascii=False)
            response_data = self._truncate_payload(response_data)

            log_event(
                self.logger,
                "http",
                "response",
                level=logging.WARNING if not response.ok else logging.INFO,
                method=request.method,
                url=request.url,
                status_code=response.status_code,
                ok=response.ok,
            )
            self.logger.info("response_body=%s", response_data)
        except Exception as e:
            log_event(
                self.logger,
                "http",
                "logging_failed",
                level=logging.ERROR,
                error_type=type(e).__name__,
                error=str(e),
            )
