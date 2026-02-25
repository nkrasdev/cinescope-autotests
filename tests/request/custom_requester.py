import contextlib
import json
import logging
import os
import time
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import allure
import requests
from pydantic import ValidationError

from tests.models.response_models import ErrorResponse
from tests.utils.logging_utils import log_event


class CustomRequester:
    base_headers = {"Content-Type": "application/json", "Accept": "application/json"}
    RETRYABLE_EXCEPTIONS = (requests.exceptions.Timeout, requests.exceptions.ConnectionError)
    MAX_REQUEST_ATTEMPTS = 2
    RETRY_DELAY_SECONDS = 1.0
    SLEEP_FN = staticmethod(time.sleep)
    SENSITIVE_FIELDS = {
        "authorization",
        "email",
        "password",
        "passwordrepeat",
        "token",
        "access_token",
        "refresh_token",
        "apikey",
        "api_key",
        "secret",
        "cardnumber",
        "securitycode",
        "cvc",
        "cvv",
    }

    def __init__(self, session: requests.Session, base_url: str):
        self.session = session
        self.base_url = base_url.rstrip("/")
        self.session.headers.update(self.base_headers)
        self.logger = logging.getLogger(self.__class__.__name__)

    def _build_url(self, endpoint: str) -> str:
        normalized_endpoint = endpoint if endpoint.startswith("/") else f"/{endpoint}"
        return f"{self.base_url}{normalized_endpoint}"

    def _send_request(
        self,
        method: str,
        endpoint: str,
        params: dict | None = None,
        data: Any = None,
        json_data: Any = None,
        **kwargs,
    ) -> requests.Response:
        url = self._build_url(endpoint)

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
                    self.SLEEP_FN(self.RETRY_DELAY_SECONDS)

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

    @staticmethod
    def parse_error_response(response: requests.Response) -> ErrorResponse:
        try:
            payload = response.json()
        except (ValueError, json.JSONDecodeError):
            message = response.text.strip() or response.reason or "Request failed with non-JSON response."
            return ErrorResponse(statusCode=response.status_code, message=message)

        if isinstance(payload, dict):
            normalized_payload = dict(payload)
            normalized_payload.setdefault("statusCode", response.status_code)
            normalized_payload.setdefault("message", response.reason or "Request failed.")
            try:
                return ErrorResponse.model_validate(normalized_payload)
            except ValidationError:
                return ErrorResponse(statusCode=response.status_code, message=response.text or str(normalized_payload))

        return ErrorResponse(statusCode=response.status_code, message=str(payload))

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
        log_context: dict[str, Any] = {"status_code": error.statusCode, "error": error.message}
        log_context.update(context)
        log_event(self.logger, domain, action, level=level, **log_context)
        return error

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

    @classmethod
    def _is_sensitive_field(cls, key: str) -> bool:
        normalized = key.lower().replace("-", "").replace("_", "")
        return any(field in normalized for field in cls.SENSITIVE_FIELDS)

    @classmethod
    def _redact_mapping_like(cls, payload: Any) -> Any:
        if isinstance(payload, dict):
            redacted: dict[Any, Any] = {}
            for key, value in payload.items():
                key_str = str(key)
                if cls._is_sensitive_field(key_str):
                    redacted[key] = "<redacted>"
                    continue
                redacted[key] = cls._redact_mapping_like(value)
            return redacted
        if isinstance(payload, list):
            return [cls._redact_mapping_like(item) for item in payload]
        return payload

    @classmethod
    def _sanitize_request_body(cls, body: str) -> str:
        stripped = body.strip()
        if not stripped:
            return body

        with contextlib.suppress(json.JSONDecodeError):
            parsed = json.loads(stripped)
            redacted = cls._redact_mapping_like(parsed)
            return json.dumps(redacted, ensure_ascii=False)

        parsed_query = parse_qsl(stripped, keep_blank_values=True)
        if parsed_query:
            redacted_query = [
                (key, "<redacted>" if cls._is_sensitive_field(key) else value) for key, value in parsed_query
            ]
            return urlencode(redacted_query, doseq=True)

        return body

    @classmethod
    def _sanitize_url(cls, url: str) -> str:
        split = urlsplit(url)
        if not split.query:
            return url

        query_pairs = parse_qsl(split.query, keep_blank_values=True)
        if not query_pairs:
            return url

        redacted_query = [(k, "<redacted>" if cls._is_sensitive_field(k) else v) for k, v in query_pairs]
        return urlunsplit(
            (split.scheme, split.netloc, split.path, urlencode(redacted_query, doseq=True), split.fragment)
        )

    @staticmethod
    def _escape_single_quotes(value: str) -> str:
        return value.replace("'", "'\"'\"'")

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
            sanitized_url = self._sanitize_url(request.url)

            body = ""
            if hasattr(request, "body") and request.body is not None:
                raw_body = request.body.decode("utf-8") if isinstance(request.body, bytes) else str(request.body)
                if raw_body and raw_body != "{}":
                    sanitized_body = self._sanitize_request_body(raw_body)
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
                url=sanitized_url,
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
