import logging
import os
import json
import allure
import requests

class CustomRequester:

    base_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    def __init__(self, session, base_url):
        self.session = session
        self.base_url = base_url
        self.session.headers.update(self.base_headers)
        self.logger = logging.getLogger(__name__)

    def _send_request(self, method, endpoint, params=None, json_data=None, **kwargs):
        url = f"{self.base_url}{endpoint}"

        expected_status = kwargs.pop('expected_status', None)

        request_kwargs = kwargs
        if params:
            request_kwargs['params'] = params
        if json_data:
            request_kwargs['json'] = json_data

        step_name = f"Выполнение {method.upper()} запроса на {url}"
        with allure.step(step_name):
            self._attach_request_details(method, url, params, json_data)

            response = self.session.request(method, url, **request_kwargs)
            self._attach_response_details(response)
            self._validate_status_code(response, expected_status)

            return response

    def get(self, endpoint, params=None, **kwargs):
        return self._send_request("GET", endpoint, params=params, **kwargs)

    def post(self, endpoint, data=None, **kwargs):
        return self._send_request("POST", endpoint, json_data=data, **kwargs)

    def patch(self, endpoint, data=None, **kwargs):
        return self._send_request("PATCH", endpoint, json_data=data, **kwargs)

    def delete(self, endpoint, data=None, **kwargs):
        return self._send_request("DELETE", endpoint, json_data=data, **kwargs)

    def _update_session_headers(self, **kwargs):
        self.session.headers.update(kwargs)

    def _validate_status_code(self, response: requests.Response, expected_status: int):
        if expected_status:
            assert response.status_code == expected_status, \
                f"Ожидался статус-код {expected_status}, но получен {response.status_code}. " \
                f"Тело ответа: {response.text}"

    def _attach_request_details(self, method, url, params, json_data):
        allure.attach(
            body=f"{method.upper()} {url}",
            name="Request Line",
            attachment_type=allure.attachment_type.TEXT
        )
        if params:
            allure.attach(
                body=json.dumps(params, indent=4, ensure_ascii=False),
                name="Query Parameters",
                attachment_type=allure.attachment_type.JSON
            )
        if json_data:
            allure.attach(
                body=json.dumps(json_data, indent=4, ensure_ascii=False),
                name="Request Body",
                attachment_type=allure.attachment_type.JSON
            )

    def _attach_response_details(self, response):
        status_code = response.status_code
        allure.attach(
            body=str(status_code),
            name="Response Status Code",
            attachment_type=allure.attachment_type.TEXT
        )
        try:
            response_body = json.dumps(response.json(), indent=4, ensure_ascii=False)
            attachment_type = allure.attachment_type.JSON
        except (json.JSONDecodeError, AttributeError):
            response_body = response.text
            attachment_type = allure.attachment_type.TEXT

        allure.attach(
            body=response_body,
            name="Response Body",
            attachment_type=attachment_type
        )

    def log_request_and_response(self, response):
        try:
            request = response.request
            GREEN = '\033[32m'
            RED = '\033[31m'
            RESET = '\033[0m'
            headers = " \\\n".join([f"-H '{header}: {value}'" for header, value in request.headers.items()])
            full_test_name = f"pytest {os.environ.get('PYTEST_CURRENT_TEST', '').replace(' (call)', '')}"

            body = ""
            if hasattr(request, 'body') and request.body is not None:
                if isinstance(request.body, bytes):
                    body = request.body.decode('utf-8')
                body = f"-d '{body}' \n" if body != '{}' else ''

            self.logger.info(f"\n{'=' * 40} REQUEST {'=' * 40}")
            self.logger.info(
                f"{GREEN}{full_test_name}{RESET}\n"
                f"curl -X {request.method} '{request.url}' \\\n"
                f"{headers} \\\n"
                f"{body}"
            )

            response_data = response.text
            try:
                response_data = json.dumps(json.loads(response.text), indent=4, ensure_ascii=False)
            except json.JSONDecodeError:
                pass

            self.logger.info(f"\n{'=' * 40} RESPONSE {'=' * 40}")
            if not response.ok:
                self.logger.info(
                    f"\tSTATUS_CODE: {RED}{response.status_code}{RESET}\n"
                    f"\tDATA: {RED}{response_data}{RESET}"
                )
            else:
                self.logger.info(
                    f"\tSTATUS_CODE: {GREEN}{response.status_code}{RESET}\n"
                    f"\tDATA:\n{response_data}"
                )
            self.logger.info(f"{'=' * 80}\n")
        except Exception as e:
            self.logger.error(f"\nLogging failed: {type(e)} - {e}")
