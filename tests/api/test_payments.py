import logging

import allure
import pytest_check as check

from tests.constants.payment_data import PAYMENT_CARD, PAYMENT_TICKETS_AMOUNT
from tests.models.payment_models import PaymentRegistryResponse, PaymentResponse, PaymentsListResponse, PaymentStatus
from tests.models.response_models import LoginResponse, MoviesList
from tests.utils.decorators import allure_test_details

LOGGER = logging.getLogger(__name__)


def _get_movie_id(api_manager) -> int:
    response = api_manager.movies_api.get_movies()
    assert isinstance(response, MoviesList)
    assert response.movies, "Список фильмов пуст, невозможно выполнить оплату"
    return response.movies[0].id


@allure.epic("Оплата")
@allure.feature("Платежи")
class TestPayments:
    @allure_test_details(
        story="Создание оплаты",
        title="Тест успешной оплаты",
        description="Проверка, что пользователь может успешно оплатить билет.",
        severity=allure.severity_level.CRITICAL,
    )
    def test_create_payment_success(self, new_registered_user):
        LOGGER.info("Запуск теста: test_create_payment_success")
        api_manager, user_payload = new_registered_user
        with allure.step("Логин пользователя"):
            api_manager.auth_api.login(email=user_payload.email, password=user_payload.password, expected_status=201)
        movie_id = _get_movie_id(api_manager)

        payload = {"movieId": movie_id, "amount": PAYMENT_TICKETS_AMOUNT, "card": PAYMENT_CARD}
        with allure.step("Создание платежа"):
            response = api_manager.payment_api.create_payment(payload, expected_status=201)
        check.is_true(
            isinstance(response, PaymentRegistryResponse),
            f"Ожидался объект PaymentRegistryResponse, но получен {type(response)}",
        )
        if isinstance(response, PaymentRegistryResponse):
            check.equal(response.status, PaymentStatus.SUCCESS)

    @allure_test_details(
        story="Создание оплаты",
        title="Тест ошибки оплаты без авторизации",
        description="Проверка, что без токена авторизации платеж не создается.",
        severity=allure.severity_level.NORMAL,
    )
    def test_create_payment_unauthorized(self, api_manager):
        LOGGER.info("Запуск теста: test_create_payment_unauthorized")
        movie_id = _get_movie_id(api_manager)
        payload = {"movieId": movie_id, "amount": PAYMENT_TICKETS_AMOUNT, "card": PAYMENT_CARD}
        with allure.step("Создание платежа без авторизации"):
            response = api_manager.payment_api.create_payment(payload, expected_status=401)
        check.equal(response.status_code, 401)

    @allure_test_details(
        story="Получение платежей",
        title="Тест получения платежей текущего пользователя",
        description="Проверка, что пользователь может получить свои платежи.",
        severity=allure.severity_level.NORMAL,
    )
    def test_get_current_user_payments(self, new_registered_user):
        LOGGER.info("Запуск теста: test_get_current_user_payments")
        api_manager, user_payload = new_registered_user
        with allure.step("Логин пользователя"):
            api_manager.auth_api.login(email=user_payload.email, password=user_payload.password, expected_status=201)
        movie_id = _get_movie_id(api_manager)
        payload = {"movieId": movie_id, "amount": PAYMENT_TICKETS_AMOUNT, "card": PAYMENT_CARD}
        api_manager.payment_api.create_payment(payload, expected_status=201)

        with allure.step("Запрос платежей текущего пользователя"):
            payments = api_manager.payment_api.get_current_user_payments(expected_status=200)
        check.is_true(isinstance(payments, list), f"Ожидался список PaymentResponse, но получен {type(payments)}")
        if isinstance(payments, list) and payments:
            check.is_true(isinstance(payments[0], PaymentResponse))

    @allure_test_details(
        story="Получение платежей",
        title="Тест получения платежей пользователя администратором",
        description="Проверка, что администратор может получить платежи конкретного пользователя.",
        severity=allure.severity_level.NORMAL,
    )
    def test_admin_get_user_payments(self, new_registered_user, admin_api_manager):
        LOGGER.info("Запуск теста: test_admin_get_user_payments")
        api_manager, user_payload = new_registered_user
        with allure.step("Логин пользователя"):
            login_response = api_manager.auth_api.login(
                email=user_payload.email, password=user_payload.password, expected_status=201
            )
        assert isinstance(login_response, LoginResponse)
        user_id = login_response.user.id

        movie_id = _get_movie_id(api_manager)
        payload = {"movieId": movie_id, "amount": PAYMENT_TICKETS_AMOUNT, "card": PAYMENT_CARD}
        api_manager.payment_api.create_payment(payload, expected_status=201)

        with allure.step("Запрос платежей пользователя администратором"):
            payments = admin_api_manager.payment_api.get_user_payments(user_id=user_id, expected_status=200)
        check.is_true(isinstance(payments, list), f"Ожидался список PaymentResponse, но получен {type(payments)}")

    @allure_test_details(
        story="Получение платежей",
        title="Тест получения всех платежей администратором",
        description="Проверка, что администратор может получить все платежи.",
        severity=allure.severity_level.NORMAL,
    )
    def test_admin_get_all_payments(self, admin_api_manager):
        LOGGER.info("Запуск теста: test_admin_get_all_payments")
        with allure.step("Запрос списка всех платежей"):
            response = admin_api_manager.payment_api.get_all_payments(expected_status=200)
        check.is_true(
            isinstance(response, PaymentsListResponse),
            f"Ожидался объект PaymentsListResponse, но получен {type(response)}",
        )
