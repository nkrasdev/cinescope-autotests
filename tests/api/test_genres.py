import allure

from tests.models.response_models import ErrorResponse, GenreResponse
from tests.utils.decorators import allure_test_details


@allure.epic("Жанры")
@allure.feature("Жанры фильмов")
class TestGenres:
    @allure_test_details(
        story="Получение жанров",
        title="Проверка получения списка жанров",
        description="Проверка, что API возвращает список жанров.",
        severity=allure.severity_level.NORMAL,
    )
    def test_get_genres_list(self, api_manager):
        with allure.step("Запрос списка жанров"):
            response = api_manager.movies_api.get_genres(expected_status=200)
        assert isinstance(response, list), f"Ожидался список жанров, но получен {type(response)}"
        if response:
            assert isinstance(response[0], GenreResponse)

    @allure_test_details(
        story="Получение жанра",
        title="Проверка получения жанра по ID",
        description="Проверка, что API возвращает жанр по его ID.",
        severity=allure.severity_level.NORMAL,
    )
    def test_get_genre_by_id(self, api_manager):
        genres = api_manager.movies_api.get_genres(expected_status=200)
        assert isinstance(genres, list) and genres
        genre_id = genres[0].id

        with allure.step("Запрос жанра по ID"):
            response = api_manager.movies_api.get_genre_by_id(genre_id, expected_status=200)
        assert isinstance(response, GenreResponse), f"Ожидался объект GenreResponse, но получен {type(response)}"
        assert response.id == genre_id

    @allure_test_details(
        story="Создание жанра",
        title="Проверка создания и удаления жанра",
        description="Проверка, что администратор может создать и удалить жанр.",
        severity=allure.severity_level.NORMAL,
    )
    def test_create_and_delete_genre(self, genre_factory, faker_instance):
        with allure.step("Создание жанра"):
            created_genre = genre_factory.create(f"Genre {faker_instance.unique.word()}")
        with allure.step("Удаление жанра"):
            deleted_genre = genre_factory.delete(created_genre.id)

        assert deleted_genre.id == created_genre.id


@allure.epic("Жанры")
@allure.feature("Жанры фильмов")
class TestGenreErrors:
    @allure_test_details(
        story="Ошибки создания жанра",
        title="Проверка ошибки создания жанра без авторизации",
        description="Проверка, что неавторизованный запрос на создание жанра получает 401.",
        severity=allure.severity_level.NORMAL,
    )
    def test_create_genre_unauthorized(self, api_manager, faker_instance):
        genre_payload = {"name": f"Genre {faker_instance.unique.word()}"}
        with allure.step("Создание жанра без токена авторизации"):
            response = api_manager.movies_api.create_genre(genre_payload, expected_status=401)
        assert isinstance(response, ErrorResponse), f"Ожидался ErrorResponse, получен {type(response)}"
        assert response.status_code == 401

    @allure_test_details(
        story="Ошибки удаления жанра",
        title="Проверка ошибки удаления жанра без авторизации",
        description="Проверка, что неавторизованный запрос на удаление жанра получает 401.",
        severity=allure.severity_level.NORMAL,
    )
    def test_delete_genre_unauthorized(self, api_manager, genre_factory, faker_instance):
        created_genre = genre_factory.create(f"Genre {faker_instance.unique.word()}")

        with allure.step("Попытка удалить жанр без токена авторизации"):
            response = api_manager.movies_api.delete_genre(created_genre.id, expected_status=401)
        assert isinstance(response, ErrorResponse), f"Ожидался ErrorResponse, получен {type(response)}"
        assert response.status_code == 401
