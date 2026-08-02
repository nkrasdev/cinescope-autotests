from datetime import datetime

import allure

from tests.clients.api_manager import ApiManager
from tests.constants.endpoints import NON_EXISTENT_ID
from tests.models.movie_models import Genre, Movie
from tests.models.request_models import MovieCreate
from tests.models.response_models import ErrorResponse
from tests.utils.decorators import allure_test_details


@allure.epic("Фильмы")
@allure.feature("Моки")
class TestMockingExamples:
    @allure_test_details(
        story="Использование мока для изоляции сервисов",
        title="Проверка удаления несуществующего фильма, полученного из мока",
        description="""
        Этот тест демонстрирует использование мока для симуляции ответа от сервиса.
        Шаги:
        1. Мокируется метод `create_movie` для возврата заранее определенного объекта фильма.
        2. Вызывается метод `create_movie` - он возвращает мок-объект без реального запроса к API.
        3. Вызывается метод `delete_movie` с ID из мок-объекта.
        4. Проверяется, что API удаления возвращает ошибку 404, так как фильма с таким ID на самом деле не существует.
        """,
        severity=allure.severity_level.NORMAL,
    )
    def test_delete_movie_from_mocked_creation(self, admin_api_manager: ApiManager, movie_payload: MovieCreate, mocker):
        with allure.step("1. Подготовка данных для мока на основе фикстуры 'movie_payload'"):
            fake_movie_id = NON_EXISTENT_ID
            fake_movie = Movie.model_validate(
                {
                    "id": fake_movie_id,
                    "name": movie_payload.name,
                    "description": movie_payload.description,
                    "price": movie_payload.price,
                    "location": movie_payload.location,
                    "published": movie_payload.published,
                    "genre_id": movie_payload.genre_id,
                    "image_url": None,
                    "genre": Genre(name="Жанр из мока"),
                    "created_at": datetime.now(),
                    "rating": 0.0,
                }
            )

        with allure.step("2. Мокирование метода 'create_movie'"):
            mocker.patch.object(admin_api_manager.movies_api, "create_movie", return_value=fake_movie)

        with allure.step("3. 'Создание' фильма (на самом деле вызов мока с данными из фикстуры)"):
            created_movie_from_mock = admin_api_manager.movies_api.create_movie(movie_data=movie_payload)

            assert isinstance(created_movie_from_mock, Movie), (
                f"Мок должен был вернуть объект Movie, а не {type(created_movie_from_mock)}"
            )
            assert created_movie_from_mock.id == fake_movie_id
            assert created_movie_from_mock.name == movie_payload.name

            with allure.step("4. Попытка удалить реально несуществующий фильм по ID из мока"):
                delete_response = admin_api_manager.movies_api.delete_movie(
                    movie_id=created_movie_from_mock.id, expected_status=404
                )

            with allure.step("5. Проверка, что API вернуло ошибку 404 Not Found"):
                assert isinstance(delete_response, ErrorResponse), (
                    f"Ожидался объект ErrorResponse, но получен {type(delete_response)}"
                )
                assert delete_response.status_code == 404
                assert delete_response.message == "Фильм не найден"
