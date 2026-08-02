from collections.abc import Mapping
from typing import Any

import allure
import pytest

from tests.constants.endpoints import NON_EXISTENT_ID
from tests.constants.payment_data import PAYMENT_CARD, PAYMENT_TICKETS_AMOUNT
from tests.models.payment_models import PaymentResponse, PaymentResult, PaymentsPage, PaymentStatus
from tests.models.response_models import ErrorResponse, LoginResponse
from tests.utils.decorators import allure_test_details


def _create_payment_and_get_status(api_manager, payment_payload: Mapping[str, Any]) -> PaymentStatus:
    response = api_manager.payment_api.create_payment(payment_payload, expected_status=None)
    assert isinstance(response, PaymentResult), f"Ожидался объект PaymentResult, но получен {type(response)}"
    return response.status


@allure.epic("Оплата")
@allure.feature("Платежи")
class TestPayments:
    @allure_test_details(
        story="Создание оплаты",
        title="Проверка успешной оплаты",
        description="Проверка, что пользователь может успешно оплатить билет.",
        severity=allure.severity_level.CRITICAL,
    )
    def test_create_payment_success(self, new_registered_user, created_movie):
        api_manager, user_payload = new_registered_user
        with allure.step("Логин пользователя"):
            api_manager.auth_api.login(email=user_payload.email, password=user_payload.password)
        movie_id = created_movie.id

        payment_payload = {"movieId": movie_id, "amount": PAYMENT_TICKETS_AMOUNT, "card": PAYMENT_CARD}
        with allure.step("Создание платежа"):
            payment_status = _create_payment_and_get_status(api_manager, payment_payload)
        if payment_status == PaymentStatus.INVALID_CARD:
            pytest.xfail("DEV payment service currently returns INVALID_CARD for test cards")
        assert payment_status == PaymentStatus.SUCCESS

    @allure_test_details(
        story="Создание оплаты",
        title="Проверка ошибки оплаты без авторизации",
        description="Проверка, что без токена авторизации платеж не создается.",
        severity=allure.severity_level.NORMAL,
    )
    def test_create_payment_unauthorized(self, api_manager, created_movie):
        movie_id = created_movie.id
        payment_payload = {"movieId": movie_id, "amount": PAYMENT_TICKETS_AMOUNT, "card": PAYMENT_CARD}
        with allure.step("Создание платежа без авторизации"):
            response = api_manager.payment_api.create_payment(payment_payload, expected_status=401)
        assert isinstance(response, ErrorResponse), f"Ожидался ErrorResponse, получен {type(response)}"
        assert response.status_code == 401

    @allure_test_details(
        story="Получение платежей",
        title="Проверка получения платежей текущего пользователя",
        description="Проверка, что пользователь может получить свои платежи.",
        severity=allure.severity_level.NORMAL,
    )
    def test_get_current_user_payments(self, new_registered_user, created_movie):
        api_manager, user_payload = new_registered_user
        with allure.step("Логин пользователя"):
            api_manager.auth_api.login(email=user_payload.email, password=user_payload.password)
        movie_id = created_movie.id
        payment_payload = {"movieId": movie_id, "amount": PAYMENT_TICKETS_AMOUNT, "card": PAYMENT_CARD}
        _create_payment_and_get_status(api_manager, payment_payload)

        with allure.step("Запрос платежей текущего пользователя"):
            payments = api_manager.payment_api.get_current_user_payments(expected_status=200)
        assert isinstance(payments, list), f"Ожидался список PaymentResponse, но получен {type(payments)}"
        if payments:
            assert isinstance(payments[0], PaymentResponse)

    @allure_test_details(
        story="Получение платежей",
        title="Проверка получения платежей пользователя администратором",
        description="Проверка, что администратор может получить платежи конкретного пользователя.",
        severity=allure.severity_level.NORMAL,
    )
    def test_admin_get_user_payments(self, new_registered_user, admin_api_manager, created_movie):
        api_manager, user_payload = new_registered_user
        with allure.step("Логин пользователя"):
            login_response = api_manager.auth_api.login(email=user_payload.email, password=user_payload.password)
        assert isinstance(login_response, LoginResponse)
        user_id = login_response.user.id

        movie_id = created_movie.id
        payment_payload = {"movieId": movie_id, "amount": PAYMENT_TICKETS_AMOUNT, "card": PAYMENT_CARD}
        _create_payment_and_get_status(api_manager, payment_payload)

        with allure.step("Запрос платежей пользователя администратором"):
            payments = admin_api_manager.payment_api.get_user_payments(user_id=user_id, expected_status=200)
        assert isinstance(payments, list), f"Ожидался список PaymentResponse, но получен {type(payments)}"

    @allure_test_details(
        story="Получение платежей",
        title="Проверка получения всех платежей администратором",
        description="Проверка, что администратор может получить все платежи.",
        severity=allure.severity_level.NORMAL,
    )
    def test_admin_get_all_payments(self, admin_api_manager):
        with allure.step("Запрос списка всех платежей"):
            response = admin_api_manager.payment_api.get_all_payments(expected_status=200)
        assert isinstance(response, PaymentsPage), f"Ожидался объект PaymentsPage, но получен {type(response)}"


@allure.epic("Оплата")
@allure.feature("Платежи")
class TestPaymentErrors:
    @allure_test_details(
        story="Создание оплаты",
        title="Проверка ошибки оплаты для несуществующего фильма",
        description="Проверка, что API возвращает 404 при попытке оплатить несуществующий фильм.",
        severity=allure.severity_level.NORMAL,
    )
    def test_create_payment_movie_not_found(self, new_registered_user):
        api_manager, user_payload = new_registered_user
        with allure.step("Логин пользователя"):
            api_manager.auth_api.login(email=user_payload.email, password=user_payload.password)
        payment_payload = {"movieId": NON_EXISTENT_ID, "amount": PAYMENT_TICKETS_AMOUNT, "card": PAYMENT_CARD}
        with allure.step("Попытка создать платёж для несуществующего фильма"):
            response = api_manager.payment_api.create_payment(payment_payload, expected_status=404)
        assert isinstance(response, ErrorResponse), f"Ожидался ErrorResponse, получен {type(response)}"
        assert response.status_code == 404

    @allure_test_details(
        story="Получение платежей",
        title="Проверка ошибки получения платежей без авторизации",
        description="Проверка, что GET /user возвращает 401 без токена авторизации.",
        severity=allure.severity_level.NORMAL,
    )
    def test_get_current_user_payments_unauthorized(self, api_manager):
        with allure.step("Запрос платежей без авторизации"):
            response = api_manager.payment_api.get_current_user_payments(expected_status=401)
        assert isinstance(response, ErrorResponse), f"Ожидался ErrorResponse, получен {type(response)}"
        assert response.status_code == 401

    @allure_test_details(
        story="Получение платежей",
        title="Проверка ошибки получения платежей пользователя по ID без авторизации",
        description="Проверка, что GET /user/{userId} возвращает 401 без токена авторизации.",
        severity=allure.severity_level.NORMAL,
    )
    def test_get_user_payments_by_id_unauthorized(self, api_manager):
        with allure.step("Запрос платежей пользователя без авторизации"):
            response = api_manager.payment_api.get_user_payments(
                user_id="00000000-0000-0000-0000-000000000000", expected_status=401
            )
        assert isinstance(response, ErrorResponse), f"Ожидался ErrorResponse, получен {type(response)}"
        assert response.status_code == 401

    @allure_test_details(
        story="Получение платежей",
        title="Проверка ошибки получения платежей пользователя обычным пользователем",
        description="Проверка, что GET /user/{userId} возвращает 403 для пользователя без роли ADMIN.",
        severity=allure.severity_level.NORMAL,
    )
    def test_get_user_payments_by_id_forbidden(self, new_registered_user):
        api_manager, user_payload = new_registered_user
        with allure.step("Логин обычного пользователя"):
            login_response = api_manager.auth_api.login(email=user_payload.email, password=user_payload.password)
        assert isinstance(login_response, LoginResponse)
        user_id = login_response.user.id

        with allure.step("Попытка получить платежи по userId от имени обычного пользователя"):
            response = api_manager.payment_api.get_user_payments(user_id=user_id, expected_status=403)
        assert isinstance(response, ErrorResponse), f"Ожидался ErrorResponse, получен {type(response)}"
        assert response.status_code == 403

    @allure_test_details(
        story="Получение платежей",
        title="Проверка ошибки получения платежей несуществующего пользователя",
        description="Проверка, что GET /user/{userId} возвращает 404 для несуществующего пользователя.",
        severity=allure.severity_level.NORMAL,
    )
    def test_get_user_payments_by_id_not_found(self, admin_api_manager):
        with allure.step("Запрос платежей несуществующего пользователя"):
            response = admin_api_manager.payment_api.get_user_payments(
                user_id="00000000-0000-0000-0000-000000000000", expected_status=404
            )
        assert isinstance(response, ErrorResponse), f"Ожидался ErrorResponse, получен {type(response)}"
        assert response.status_code == 404

    @allure_test_details(
        story="Получение платежей",
        title="Проверка получения всех платежей без авторизации",
        description="Проверка, что GET /find-all возвращает 401 без токена авторизации.",
        severity=allure.severity_level.NORMAL,
    )
    def test_get_all_payments_unauthorized(self, api_manager):
        with allure.step("Запрос всех платежей без авторизации"):
            response = api_manager.payment_api.get_all_payments(expected_status=401)
        assert isinstance(response, ErrorResponse), f"Ожидался ErrorResponse, получен {type(response)}"
        assert response.status_code == 401

    @allure_test_details(
        story="Получение платежей",
        title="Проверка ошибки получения всех платежей обычным пользователем",
        description="Проверка, что GET /find-all возвращает 403 для пользователя без роли ADMIN.",
        severity=allure.severity_level.NORMAL,
    )
    def test_get_all_payments_forbidden(self, new_registered_user):
        api_manager, user_payload = new_registered_user
        with allure.step("Логин обычного пользователя"):
            api_manager.auth_api.login(email=user_payload.email, password=user_payload.password)
        with allure.step("Запрос всех платежей от обычного пользователя"):
            response = api_manager.payment_api.get_all_payments(expected_status=403)
        assert isinstance(response, ErrorResponse), f"Ожидался ErrorResponse, получен {type(response)}"
        assert response.status_code == 403


@allure.epic("Оплата")
@allure.feature("Поиск платежей")
class TestPaymentQueries:
    @allure_test_details(
        story="Фильтрация платежей",
        title="Проверка получения всех платежей с фильтром по статусу",
        description="Проверка, что фильтр status работает в GET /find-all.",
        severity=allure.severity_level.MINOR,
    )
    def test_get_all_payments_filter_by_status(self, admin_api_manager):
        query_params = {"status": PaymentStatus.SUCCESS.value}
        with allure.step(f"Запрос платежей с фильтром status={query_params['status']}"):
            response = admin_api_manager.payment_api.get_all_payments(params=query_params, expected_status=200)
        assert isinstance(response, PaymentsPage), f"Ожидался PaymentsPage, получен {type(response)}"
        for payment in response.payments:
            assert payment.status == PaymentStatus.SUCCESS

    @allure_test_details(
        story="Фильтрация платежей",
        title="Проверка получения всех платежей с пагинацией",
        description="Проверка, что параметры page и pageSize работают в GET /find-all.",
        severity=allure.severity_level.MINOR,
    )
    def test_get_all_payments_with_pagination(self, admin_api_manager):
        page_size = 5
        query_params = {"page": 1, "pageSize": page_size}
        with allure.step(f"Запрос платежей с пагинацией: {query_params}"):
            response = admin_api_manager.payment_api.get_all_payments(params=query_params, expected_status=200)
        assert isinstance(response, PaymentsPage), f"Ожидался PaymentsPage, получен {type(response)}"
        assert len(response.payments) <= page_size
        assert response.page == 1
        assert response.page_size == page_size
