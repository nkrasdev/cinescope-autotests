import allure
import pytest

from tests.constants.endpoints import NON_EXISTENT_ID
from tests.models.movie_models import MovieWithReviews
from tests.models.response_models import ErrorResponse
from tests.utils.decorators import allure_test_details


@allure.epic("Фильмы")
@allure.feature("Получение фильма по ID")
class TestGetMovieById:
    @allure_test_details(
        story="Успешное получение фильма по ID",
        title="Проверка успешного получения существующего фильма по его ID",
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
        with allure.step(f"Отправка запроса на получение фильма с ID: {movie_id}"):
            fetched_movie_response = admin_api_manager.movies_api.get_movie_by_id(movie_id, expected_status=200)

        with allure.step("Проверка, что данные полученного фильма соответствуют ожидаемым"):
            assert isinstance(fetched_movie_response, MovieWithReviews), (
                f"Ожидался объект MovieWithReviews, но получен {type(fetched_movie_response)}"
            )
            assert fetched_movie_response.id == created_movie.id
            assert fetched_movie_response.name == created_movie.name
            assert fetched_movie_response.description == created_movie.description
            assert fetched_movie_response.price == created_movie.price
            assert fetched_movie_response.location == created_movie.location
            assert fetched_movie_response.genre_id == created_movie.genre_id
            assert fetched_movie_response.published == created_movie.published
            assert fetched_movie_response.reviews == [], "У нового фильма не должно быть отзывов"

    @allure_test_details(
        story="Попытка получения несуществующего фильма",
        title="Проверка ошибки получения фильма с несуществующим ID",
        description="Проверка, что система возвращает ошибку 404 Not Found при запросе фильма с ID, которого нет в базе.",
        severity=allure.severity_level.NORMAL,
    )
    def test_get_movie_not_found(self, admin_api_manager):
        movie_id = NON_EXISTENT_ID
        with allure.step(f"Попытка получения фильма с несуществующим ID: {movie_id}"):
            response = admin_api_manager.movies_api.get_movie_by_id(movie_id, expected_status=404)
        with allure.step("Проверка ответа об ошибке 'Фильм не найден'"):
            assert isinstance(response, ErrorResponse), f"Ожидался объект ErrorResponse, но получен {type(response)}"
            assert response.status_code == 404
            assert response.message == "Фильм не найден"

    @allure_test_details(
        story="Попытка получения несуществующего фильма",
        title="Проверка ошибки получения фильма с невалидным (отрицательным или 0) ID",
        description="Проверка, что система возвращает ошибку 404 Not Found при запросе фильма с ID <= 0.",
        severity=allure.severity_level.MINOR,
    )
    @pytest.mark.parametrize("invalid_id", [0, -1])
    def test_get_movie_not_found_invalid_id(self, admin_api_manager, invalid_id):
        with allure.step(f"Попытка получения фильма с невалидным ID: {invalid_id}"):
            response = admin_api_manager.movies_api.get_movie_by_id(invalid_id, expected_status=404)
        with allure.step("Проверка ответа об ошибке"):
            assert isinstance(response, ErrorResponse), f"Ожидался объект ErrorResponse, но получен {type(response)}"
            assert response.status_code == 404

    @allure_test_details(
        story="Попытка получения фильма с невалидным форматом ID",
        title="Проверка ошибки получения фильма с нецелочисленным форматом ID",
        description="Проверка, что система возвращает ошибку 400 при запросе фильма с ID неверного формата (не целое число).",
        severity=allure.severity_level.MINOR,
    )
    @pytest.mark.parametrize(
        "invalid_id, expected_status",
        [
            (" ", 404),
            pytest.param(
                "abc",
                400,
                marks=pytest.mark.xfail(reason="API returns 500 for string IDs — known server bug", strict=True),
            ),
            pytest.param(
                "null",
                400,
                marks=pytest.mark.xfail(
                    reason="API returns 500 for 'null' string ID — known server bug",
                    strict=True,
                ),
            ),
        ],
    )
    def test_get_movie_bad_request(self, admin_api_manager, invalid_id, expected_status):
        with allure.step(f"Попытка получения фильма по невалидному ID: '{invalid_id}'"):
            response = admin_api_manager.movies_api.get_movie_by_id(
                movie_id=invalid_id,
                expected_status=expected_status,
            )
        with allure.step("Проверка ответа об ошибке"):
            assert isinstance(response, ErrorResponse), f"Ожидался объект ErrorResponse, но получен {type(response)}"
            assert response.status_code == expected_status
