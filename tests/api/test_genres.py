import contextlib
import logging

import allure
import pytest_check as check

from tests.models.response_models import ErrorResponse, GenreResponse
from tests.utils.decorators import allure_test_details

LOGGER = logging.getLogger(__name__)


@allure.epic("Жанры")
@allure.feature("Жанры фильмов")
class TestGenres:
    @allure_test_details(
        story="Получение жанров",
        title="Тест получения списка жанров",
        description="Проверка, что API возвращает список жанров.",
        severity=allure.severity_level.NORMAL,
    )
    def test_get_genres_list(self, api_manager):
        with allure.step("Запрос списка жанров"):
            response = api_manager.movies_api.get_genres(expected_status=200)
        check.is_true(isinstance(response, list), f"Ожидался список жанров, но получен {type(response)}")
        if isinstance(response, list) and response:
            check.is_true(isinstance(response[0], GenreResponse))

    @allure_test_details(
        story="Получение жанра",
        title="Тест получения жанра по ID",
        description="Проверка, что API возвращает жанр по его ID.",
        severity=allure.severity_level.NORMAL,
    )
    def test_get_genre_by_id(self, api_manager):
        genres = api_manager.movies_api.get_genres(expected_status=200)
        assert isinstance(genres, list) and genres
        genre_id = genres[0].id

        with allure.step("Запрос жанра по ID"):
            response = api_manager.movies_api.get_genre_by_id(genre_id, expected_status=200)
        check.is_true(
            isinstance(response, GenreResponse), f"Ожидался объект GenreResponse, но получен {type(response)}"
        )
        if isinstance(response, GenreResponse):
            check.equal(response.id, genre_id)

    @allure_test_details(
        story="Создание жанра",
        title="Тест создания и удаления жанра",
        description="Проверка, что администратор может создать и удалить жанр.",
        severity=allure.severity_level.NORMAL,
    )
    def test_create_and_delete_genre(self, admin_api_manager, faker_instance):
        genre_id = None
        payload = {"name": f"Genre {faker_instance.unique.word()}"}
        try:
            with allure.step("Создание жанра"):
                created_genre = admin_api_manager.movies_api.create_genre(payload, expected_status=201)
            check.is_true(isinstance(created_genre, GenreResponse))
            if isinstance(created_genre, GenreResponse):
                genre_id = created_genre.id
        finally:
            if genre_id:
                admin_api_manager.movies_api.delete_genre(genre_id, expected_status=200)


@allure.epic("Жанры")
@allure.feature("Жанры фильмов")
class TestGenresNegative:
    @allure_test_details(
        story="Ошибки создания жанра",
        title="Тест ошибки создания жанра без авторизации",
        description="Проверка, что неавторизованный запрос на создание жанра получает 401.",
        severity=allure.severity_level.NORMAL,
    )
    def test_create_genre_unauthorized(self, api_manager, faker_instance):
        payload = {"name": f"Genre {faker_instance.unique.word()}"}
        with allure.step("Создание жанра без токена авторизации"):
            response = api_manager.movies_api.create_genre(payload, expected_status=401)
        check.is_true(isinstance(response, ErrorResponse), f"Ожидался ErrorResponse, получен {type(response)}")
        if isinstance(response, ErrorResponse):
            check.equal(response.statusCode, 401)

    @allure_test_details(
        story="Ошибки удаления жанра",
        title="Тест ошибки удаления жанра без авторизации",
        description="Проверка, что неавторизованный запрос на удаление жанра получает 401.",
        severity=allure.severity_level.NORMAL,
    )
    def test_delete_genre_unauthorized(self, api_manager, admin_api_manager, faker_instance):
        payload = {"name": f"Genre {faker_instance.unique.word()}"}
        genre_id = None
        try:
            created = admin_api_manager.movies_api.create_genre(payload, expected_status=201)
            assert isinstance(created, GenreResponse)
            genre_id = created.id

            with allure.step("Попытка удалить жанр без токена авторизации"):
                response = api_manager.movies_api.delete_genre(genre_id, expected_status=401)
            check.is_true(isinstance(response, ErrorResponse), f"Ожидался ErrorResponse, получен {type(response)}")
            if isinstance(response, ErrorResponse):
                check.equal(response.statusCode, 401)
        finally:
            if genre_id:
                with contextlib.suppress(AssertionError):
                    admin_api_manager.movies_api.delete_genre(genre_id, expected_status=200)
