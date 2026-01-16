import logging

import allure
import pytest_check as check

from tests.models.movie_models import Movie, Review
from tests.models.response_models import ErrorResponse, LoginResponse
from tests.utils.decorators import allure_test_details

LOGGER = logging.getLogger(__name__)


@allure.epic("Отзывы")
@allure.feature("Отзывы к фильмам")
class TestReviews:
    @allure_test_details(
        story="Получение отзывов",
        title="Тест получения списка отзывов фильма",
        description="Проверка, что API возвращает список отзывов по фильму.",
        severity=allure.severity_level.NORMAL,
    )
    def test_get_reviews(self, api_manager, created_movie: Movie):
        LOGGER.info("Запуск теста: test_get_reviews")
        with allure.step("Запрос списка отзывов"):
            response = api_manager.movies_api.get_reviews(created_movie.id, expected_status=200)
        check.is_true(isinstance(response, list), f"Ожидался список отзывов, но получен {type(response)}")

    @allure_test_details(
        story="Создание отзыва",
        title="Тест успешного создания отзыва",
        description="Проверка, что пользователь может создать отзыв к фильму.",
        severity=allure.severity_level.CRITICAL,
    )
    def test_create_review_success(self, new_registered_user, created_movie: Movie):
        LOGGER.info("Запуск теста: test_create_review_success")
        api_manager, user_payload = new_registered_user
        api_manager.auth_api.login(email=user_payload.email, password=user_payload.password, expected_status=201)
        payload = {"rating": 5, "text": "Очень хороший фильм"}

        with allure.step("Создание отзыва"):
            response = api_manager.movies_api.create_review(created_movie.id, payload, expected_status=201)

        reviews = response if isinstance(response, list) else [response]
        matches = [review for review in reviews if isinstance(review, Review) and review.text == payload["text"]]
        check.is_true(matches, "Созданный отзыв не найден в ответе")

    @allure_test_details(
        story="Создание отзыва",
        title="Тест ошибки создания повторного отзыва",
        description="Проверка, что повторное создание отзыва возвращает ошибку 409.",
        severity=allure.severity_level.NORMAL,
    )
    def test_create_review_conflict(self, new_registered_user, created_movie: Movie):
        LOGGER.info("Запуск теста: test_create_review_conflict")
        api_manager, user_payload = new_registered_user
        api_manager.auth_api.login(email=user_payload.email, password=user_payload.password, expected_status=201)
        payload = {"rating": 4, "text": "Хороший фильм"}
        api_manager.movies_api.create_review(created_movie.id, payload, expected_status=201)

        with allure.step("Попытка создать повторный отзыв"):
            response = api_manager.movies_api.create_review(created_movie.id, payload, expected_status=409)
        check.is_true(
            isinstance(response, ErrorResponse), f"Ожидался объект ErrorResponse, но получен {type(response)}"
        )

    @allure_test_details(
        story="Редактирование отзыва",
        title="Тест успешного редактирования отзыва",
        description="Проверка, что пользователь может отредактировать свой отзыв.",
        severity=allure.severity_level.NORMAL,
    )
    def test_edit_review_success(self, new_registered_user, created_movie: Movie):
        LOGGER.info("Запуск теста: test_edit_review_success")
        api_manager, user_payload = new_registered_user
        api_manager.auth_api.login(email=user_payload.email, password=user_payload.password, expected_status=201)
        api_manager.movies_api.create_review(created_movie.id, {"rating": 5, "text": "Исходный текст"})
        payload = {"rating": 3, "text": "Обновленный текст"}

        with allure.step("Редактирование отзыва"):
            response = api_manager.movies_api.edit_review(created_movie.id, payload, expected_status=200)
        check.is_true(isinstance(response, Review), f"Ожидался объект Review, но получен {type(response)}")
        if isinstance(response, Review):
            check.equal(response.text, payload["text"])

    @allure_test_details(
        story="Удаление отзыва",
        title="Тест успешного удаления отзыва",
        description="Проверка, что пользователь может удалить свой отзыв.",
        severity=allure.severity_level.NORMAL,
    )
    def test_delete_review_success(self, new_registered_user, created_movie: Movie):
        LOGGER.info("Запуск теста: test_delete_review_success")
        api_manager, user_payload = new_registered_user
        api_manager.auth_api.login(email=user_payload.email, password=user_payload.password, expected_status=201)
        api_manager.movies_api.create_review(created_movie.id, {"rating": 4, "text": "Будет удален"})

        with allure.step("Удаление отзыва"):
            response = api_manager.movies_api.delete_review(created_movie.id, expected_status=200)
        if response:
            check.is_true(isinstance(response, Review), f"Ожидался объект Review, но получен {type(response)}")

    @allure_test_details(
        story="Модерация отзывов",
        title="Тест скрытия и показа отзыва администратором",
        description="Проверка, что администратор может скрыть и показать отзыв пользователя.",
        severity=allure.severity_level.NORMAL,
    )
    def test_hide_show_review(self, new_registered_user, admin_api_manager, created_movie: Movie):
        LOGGER.info("Запуск теста: test_hide_show_review")
        api_manager, user_payload = new_registered_user
        login_response = api_manager.auth_api.login(
            email=user_payload.email, password=user_payload.password, expected_status=201
        )
        assert isinstance(login_response, LoginResponse)
        user_id = login_response.user.id
        api_manager.movies_api.create_review(created_movie.id, {"rating": 5, "text": "Для модерации"})

        with allure.step("Скрытие отзыва"):
            hidden_review = admin_api_manager.movies_api.hide_review(
                movie_id=created_movie.id, user_id=user_id, expected_status=200
            )
        check.is_true(isinstance(hidden_review, Review))

        with allure.step("Показ отзыва"):
            shown_review = admin_api_manager.movies_api.show_review(
                movie_id=created_movie.id, user_id=user_id, expected_status=200
            )
        check.is_true(isinstance(shown_review, Review))
