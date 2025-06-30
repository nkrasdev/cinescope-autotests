import allure
import pytest
import pytest_check as check
import logging

from tests.constants.endpoints import NON_EXISTENT_ID
from tests.models.movie_models import MovieWithReviews
from tests.models.response_models import ErrorResponse
from tests.utils.decorators import allure_test_details
from tests.constants.log_messages import LogMessages

LOGGER = logging.getLogger(__name__)

@allure.epic("Movies API")
@allure.feature("Получение фильма по ID")
class TestGetMovieById:

    @allure_test_details(
        story="Успешное получение фильма по ID",
        title="Тест успешного получения существующего фильма по его ID",
        description="""
        Проверка, что можно успешно получить данные существующего фильма по его ID.
        Шаги:
        1. Создание фильма через фикстуру.
        2. Отправка GET-запроса с ID созданного фильма.
        3. Проверка, что API возвращает статус 200 и корректные данные фильма.
        4. Сравнение всех полей полученного фильма с данными изначального.
        """,
        severity=allure.severity_level.CRITICAL,
    )
    def test_get_existing_movie_by_id(self, admin_api_manager, created_movie):
        movie_id = created_movie.id
        LOGGER.info(f"Запуск теста: test_get_existing_movie_by_id для ID {movie_id}")
        with allure.step(f"Отправка запроса на получение фильма с ID: {movie_id}"):
            LOGGER.info(LogMessages.Movies.ATTEMPT_GET_BY_ID.format(movie_id))
            fetched_movie_response = admin_api_manager.movies_api.get_movie_by_id(movie_id, expected_status=200)

        with allure.step("Проверка, что данные полученного фильма соответствуют ожидаемым"):
            is_movie = isinstance(fetched_movie_response, MovieWithReviews)
            check.is_true(is_movie, f"Ожидался объект MovieWithReviews, но получен {type(fetched_movie_response)}")
            if is_movie:
                LOGGER.info(LogMessages.Movies.GET_BY_ID_SUCCESS.format(fetched_movie_response.name, movie_id))
                check.equal(fetched_movie_response.id, created_movie.id)
                check.equal(fetched_movie_response.name, created_movie.name)
                check.equal(fetched_movie_response.description, created_movie.description)
                check.equal(fetched_movie_response.price, created_movie.price)
                check.equal(fetched_movie_response.location, created_movie.location)
                check.equal(fetched_movie_response.genre_id, created_movie.genre_id)
                check.is_true(fetched_movie_response.published == created_movie.published)
                check.equal(fetched_movie_response.reviews, [], "У нового фильма не должно быть отзывов")
                LOGGER.info(f"Все поля для фильма ID {movie_id} успешно проверены.")

    @allure_test_details(
        story="Попытка получения несуществующего фильма",
        title="Тест ошибки получения фильма с несуществующим ID",
        description="Этот тест проверяет, что система возвращает ошибку 404 Not Found при запросе фильма с ID, которого нет в базе.",
        severity=allure.severity_level.NORMAL,
    )
    def test_get_movie_not_found(self, admin_api_manager):
        movie_id = NON_EXISTENT_ID
        LOGGER.info(f"Запуск теста: test_get_movie_not_found для несуществующего ID {movie_id}")
        with allure.step(f"Попытка получения фильма с несуществующим ID: {movie_id}"):
            LOGGER.info(LogMessages.Movies.ATTEMPT_GET_BY_ID.format(movie_id))
            response = admin_api_manager.movies_api.get_movie_by_id(movie_id, expected_status=404)
        with allure.step("Проверка ответа об ошибке 'Фильм не найден'"):
            is_error = isinstance(response, ErrorResponse)
            check.is_true(is_error, f"Ожидался объект ErrorResponse, но получен {type(response)}")
            if is_error:
                LOGGER.info(f"Получена ожидаемая ошибка 404: {response.message}")
                check.equal(response.statusCode, 404)
                check.equal(response.message, "Фильм не найден")

    @allure_test_details(
        story="Попытка получения несуществующего фильма",
        title="Тест ошибки получения фильма с невалидным (отрицательным или 0) ID",
        description="Этот тест проверяет, что система возвращает ошибку 404 Not Found при запросе фильма с ID <= 0.",
        severity=allure.severity_level.MINOR,
    )
    @pytest.mark.parametrize("invalid_id", [0, -1])
    def test_get_movie_not_found_invalid_id(self, admin_api_manager, invalid_id):
        LOGGER.info(f"Запуск теста: test_get_movie_not_found_invalid_id с ID: {invalid_id}")
        with allure.step(f"Попытка получения фильма с невалидным ID: {invalid_id}"):
            LOGGER.info(LogMessages.Movies.ATTEMPT_GET_BY_ID.format(invalid_id))
            response = admin_api_manager.movies_api.get_movie_by_id(
                invalid_id,
                expected_status=404
            )
        with allure.step("Проверка ответа об ошибке"):
            is_error = isinstance(response, ErrorResponse)
            check.is_true(is_error, f"Ожидался объект ErrorResponse, но получен {type(response)}")
            if is_error:
                LOGGER.info(f"Получена ожидаемая ошибка 404. Ответ: {response.message}")
                check.equal(response.statusCode, 404)

    @allure_test_details(
        story="Попытка получения фильма с невалидным форматом ID",
        title="Тест ошибки получения фильма с нецелочисленным форматом ID",
        description="Этот тест проверяет, что система возвращает ошибку 400 при запросе фильма с ID неверного формата (не целое число).",
        severity=allure.severity_level.MINOR,
    )
    @pytest.mark.parametrize("invalid_id, expected_status", [
        (" ", 404),
        ("abc", 500),
        ("null", 500)
    ])
    def test_get_movie_bad_request(self, admin_api_manager, invalid_id, expected_status):
        LOGGER.info(f"Запуск теста: test_get_movie_bad_request с ID: '{invalid_id}' и ожидаемым статусом {expected_status}")
        with allure.step(f"Попытка получения фильма по невалидному ID: '{invalid_id}'"):
            LOGGER.info(f"Попытка получения фильма по ID {invalid_id}")
            response = admin_api_manager.movies_api.get_movie_by_id(
                movie_id=invalid_id,
                expected_status=expected_status,
            )
        with allure.step("Проверка ответа об ошибке"):
            is_error = isinstance(response, ErrorResponse)
            check.is_true(is_error, f"Ожидался объект ErrorResponse, но получен {type(response)}")
            if is_error:
                LOGGER.info(f"Получена ожидаемая ошибка {expected_status}. Ответ: {response.message}")
                check.equal(response.statusCode, expected_status)
