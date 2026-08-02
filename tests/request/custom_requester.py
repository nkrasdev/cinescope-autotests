import json
import logging
import os
import time
from collections.abc import Mapping
from contextlib import suppress
from typing import Any

import allure
import requests
from pydantic import ValidationError

from tests.models.response_models import ErrorResponse
from tests.utils.logging_utils import log_event
from tests.utils.sensitive_data import redact_data, sanitize_body, sanitize_url


class CustomRequester:
    BASE_HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}
    DEFAULT_TIMEOUT_SECONDS = 30
    RETRYABLE_EXCEPTIONS = (requests.exceptions.Timeout, requests.exceptions.ConnectionError)
    RETRYABLE_METHODS = frozenset({"DELETE", "GET", "HEAD", "OPTIONS", "PUT"})
    MAX_REQUEST_ATTEMPTS = 2
    RETRY_DELAY_SECONDS = 1.0
    SLEEP_FN = staticmethod(time.sleep)

    def __init__(self, session: requests.Session, base_url: str):
        self.session = session
        self.base_url = base_url.rstrip("/")
        self.session.headers.update(self.BASE_HEADERS)
        self.logger = logging.getLogger(self.__class__.__name__)

    def _build_url(self, endpoint: str) -> str:
        normalized_endpoint = endpoint if endpoint.startswith("/") else f"/{endpoint}"
        return f"{self.base_url}{normalized_endpoint}"

    def _send_request(
        self,
        method: str,
        endpoint: str,
        params: Mapping[str, Any] | None = None,
        data: Any = None,
        json_data: Any = None,
        expected_status: int | None = None,
        redact_url_path: bool = False,
        **request_options: Any,
    ) -> requests.Response:
        url = self._build_url(endpoint)
        reporting_url = sanitize_url(url, redact_path=redact_url_path)

        request_options.setdefault("timeout", self.DEFAULT_TIMEOUT_SECONDS)
        if params is not None:
            request_options["params"] = params
        if data is not None:
            request_options["data"] = data
        if json_data is not None:
            request_options["json"] = json_data

        step_name = f"Выполнение {method.upper()} запроса на {reporting_url}"
        with allure.step(step_name):
            self._attach_request_details(method, reporting_url, params, data, json_data)

            response = None
            for attempt in range(1, self.MAX_REQUEST_ATTEMPTS + 1):
                try:
                    response = self.session.request(method, url, **request_options)
                    break
                except self.RETRYABLE_EXCEPTIONS as exc:
                    if method.upper() not in self.RETRYABLE_METHODS or attempt == self.MAX_REQUEST_ATTEMPTS:
                        raise
                    log_event(
                        self.logger,
                        "http",
                        "retry",
                        level=logging.WARNING,
                        method=method.upper(),
                        url=reporting_url,
                        error_type=type(exc).__name__,
                        attempt=attempt + 1,
                        max_attempts=self.MAX_REQUEST_ATTEMPTS,
                        delay_sec=self.RETRY_DELAY_SECONDS,
                    )
                    self.SLEEP_FN(self.RETRY_DELAY_SECONDS)

            if response is None:
                raise RuntimeError(f"Не удалось выполнить запрос {method.upper()} {reporting_url}")
            self._attach_response_details(response)
            self.log_request_and_response(response, redact_url_path=redact_url_path)
            self._assert_expected_status(response, expected_status)

            return response

    def get(
        self,
        endpoint: str,
        params: Mapping[str, Any] | None = None,
        *,
        expected_status: int | None = None,
        redact_url_path: bool = False,
        **request_options: Any,
    ) -> requests.Response:
        return self._send_request(
            "GET",
            endpoint,
            params=params,
            expected_status=expected_status,
            redact_url_path=redact_url_path,
            **request_options,
        )

    def post(
        self,
        endpoint: str,
        data: Any = None,
        json: Any = None,
        *,
        expected_status: int | None = None,
        **request_options: Any,
    ) -> requests.Response:
        return self._send_request(
            "POST", endpoint, data=data, json_data=json, expected_status=expected_status, **request_options
        )

    def patch(
        self,
        endpoint: str,
        data: Any = None,
        json: Any = None,
        *,
        expected_status: int | None = None,
        **request_options: Any,
    ) -> requests.Response:
        return self._send_request(
            "PATCH", endpoint, data=data, json_data=json, expected_status=expected_status, **request_options
        )

    def put(
        self,
        endpoint: str,
        data: Any = None,
        json: Any = None,
        *,
        expected_status: int | None = None,
        **request_options: Any,
    ) -> requests.Response:
        return self._send_request(
            "PUT", endpoint, data=data, json_data=json, expected_status=expected_status, **request_options
        )

    def delete(
        self,
        endpoint: str,
        data: Any = None,
        json: Any = None,
        *,
        expected_status: int | None = None,
        **request_options: Any,
    ) -> requests.Response:
        return self._send_request(
            "DELETE", endpoint, data=data, json_data=json, expected_status=expected_status, **request_options
        )

    def _assert_expected_status(self, response: requests.Response, expected_status: int | None) -> None:
        if expected_status is None or response.status_code == expected_status:
            return

        safe_response_body = sanitize_body(response.text)
        raise AssertionError(
            f"Ожидался статус-код {expected_status}, но получен {response.status_code}. "
            f"Тело ответа: {safe_response_body}"
        )

    @staticmethod
    def parse_error_response(response: requests.Response) -> ErrorResponse:
        try:
            payload = response.json()
        except ValueError:
            message = response.text.strip() or response.reason or "Request failed with non-JSON response."
            return ErrorResponse.model_validate({"status_code": response.status_code, "message": message})

        if isinstance(payload, dict):
            normalized_payload = dict(payload)
            normalized_payload.setdefault("statusCode", response.status_code)
            normalized_payload.setdefault("message", response.reason or "Request failed.")
            try:
                return ErrorResponse.model_validate(normalized_payload)
            except ValidationError:
                return ErrorResponse.model_validate(
                    {
                        "status_code": response.status_code,
                        "message": response.text or str(normalized_payload),
                    }
                )

        return ErrorResponse.model_validate({"status_code": response.status_code, "message": str(payload)})

    def parse_and_log_error(
        self,
        response: requests.Response,
        *,
        domain: str,
        action: str,
        level: int = logging.ERROR,
        **context: Any,
    ) -> ErrorResponse:
        error = self.parse_error_response(response)
        log_context: dict[str, Any] = {"status_code": error.status_code, "error": error.message}
        log_context.update(context)
        log_event(self.logger, domain, action, level=level, **log_context)
        return error

    def _attach_request_details(
        self,
        method: str,
        url: str,
        params: Mapping[str, Any] | None,
        data: Any,
        json_data: Any,
    ) -> None:
        allure.attach(
            body=f"{method.upper()} {url}",
            name="Request Line",
            attachment_type=allure.attachment_type.TEXT,
        )
        if params is not None:
            allure.attach(
                body=json.dumps(redact_data(params), indent=4, ensure_ascii=False, default=str),
                name="Query Parameters",
                attachment_type=allure.attachment_type.JSON,
            )
        if json_data is not None:
            allure.attach(
                body=json.dumps(redact_data(json_data), indent=4, ensure_ascii=False, default=str),
                name="Request Body (JSON)",
                attachment_type=allure.attachment_type.JSON,
            )
        if data is not None:
            raw_data = data.decode("utf-8", errors="replace") if isinstance(data, bytes) else str(data)
            allure.attach(
                body=sanitize_body(raw_data),
                name="Request Body (Data)",
                attachment_type=allure.attachment_type.TEXT,
            )

    def _attach_response_details(self, response: requests.Response) -> None:
        status_code = response.status_code
        allure.attach(
            body=str(status_code),
            name="Response Status Code",
            attachment_type=allure.attachment_type.TEXT,
        )
        try:
            response_body = json.dumps(redact_data(response.json()), indent=4, ensure_ascii=False, default=str)
            attachment_type = allure.attachment_type.JSON
        except (ValueError, AttributeError):
            response_body = sanitize_body(response.text)
            attachment_type = allure.attachment_type.TEXT

        allure.attach(body=response_body, name="Response Body", attachment_type=attachment_type)

    @staticmethod
    def _truncate_payload(payload: str, max_length: int = 4000) -> str:
        if len(payload) <= max_length:
            return payload
        return f"{payload[:max_length]}... <truncated {len(payload) - max_length} chars>"

    @staticmethod
    def _escape_single_quotes(value: str) -> str:
        return value.replace("'", "'\"'\"'")

    def log_request_and_response(self, response: requests.Response, *, redact_url_path: bool = False) -> None:
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
            sanitized_url = sanitize_url(request.url or "", redact_path=redact_url_path)

            body = ""
            if hasattr(request, "body") and request.body is not None:
                raw_body = request.body.decode("utf-8") if isinstance(request.body, bytes) else str(request.body)
                if raw_body and raw_body != "{}":
                    sanitized_body = sanitize_body(raw_body)
                    escaped_body = self._escape_single_quotes(self._truncate_payload(sanitized_body))
                    body = f"-d '{escaped_body}' \n"

            log_event(
                self.logger,
                "http",
                "request",
                method=request.method,
                url=sanitized_url,
                test=full_test_name,
            )
            self.logger.info(
                "curl -X %s '%s' \\\n%s \\\n%s",
                request.method,
                sanitized_url,
                headers_str,
                body,
            )

            response_data = sanitize_body(response.text)
            with suppress(json.JSONDecodeError):
                response_data = json.dumps(redact_data(json.loads(response.text)), indent=4, ensure_ascii=False)
            response_data = self._truncate_payload(response_data)

            log_event(
                self.logger,
                "http",
                "response",
                level=logging.WARNING if not response.ok else logging.INFO,
                method=request.method,
                url=sanitized_url,
                status_code=response.status_code,
                ok=response.ok,
            )
            self.logger.info("response_body=%s", response_data)
        except Exception as exc:
            log_event(
                self.logger,
                "http",
                "logging_failed",
                level=logging.ERROR,
                error_type=type(exc).__name__,
                error=str(exc),
            )
