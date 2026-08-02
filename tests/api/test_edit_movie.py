import allure
import pytest

from tests.constants.endpoints import NON_EXISTENT_ID
from tests.models.movie_models import Movie, MovieWithReviews
from tests.models.response_models import ErrorResponse
from tests.utils.data_generator import MovieDataGenerator
from tests.utils.decorators import allure_test_details


@allure.epic("Фильмы")
@allure.feature("Редактирование фильма")
class TestEditMovie:
    @allure_test_details(
        story="Успешное редактирование фильма",
        title="Проверка успешного редактирования названия фильма",
        description="""
        Проверка, что администратор может успешно отредактировать название существующего фильма.
        Шаги:
        1. Создание фильма через фикстуру.
        2. Генерация нового названия и отправка PATCH-запроса на редактирование.
        3. Проверка, что API возвращает статус 200 и обновленные данные фильма.
        4. Проверка, что название действительно изменилось.
        5. Повторное получение фильма по ID для подтверждения сохранения изменений в базе.
        """,
        severity=allure.severity_level.CRITICAL,
    )
    def test_edit_movie_name_success(self, admin_api_manager, created_movie, faker_instance):
        movie_id = created_movie.id
        with allure.step("Подготовка: генерация нового названия для фильма"):
            new_name = "Обновленное название фильма " + MovieDataGenerator.generate_random_title(faker_instance)
            update_payload = {"name": new_name}

        with allure.step(f"Отправка запроса на редактирование фильма с ID {movie_id}"):
            edited_movie_response = admin_api_manager.movies_api.edit_movie(
                movie_id=movie_id, update_payload=update_payload, expected_status=200
            )

        with allure.step("Проверка данных в ответе API"):
            assert isinstance(edited_movie_response, Movie), (
                f"Ожидался объект Movie, но получен {type(edited_movie_response)}"
            )
            assert edited_movie_response.id == movie_id, "ID не должен меняться после редактирования"
            assert edited_movie_response.name == new_name, "Название фильма должно было обновиться"
            assert edited_movie_response.description == created_movie.description, "Описание не должно было измениться"

        with allure.step("Контрольная проверка: повторное получение фильма по ID"):
            fetched_movie_response = admin_api_manager.movies_api.get_movie_by_id(movie_id, expected_status=200)
            assert isinstance(fetched_movie_response, MovieWithReviews), (
                f"Ожидался объект MovieWithReviews, но получен {type(fetched_movie_response)}"
            )
            assert fetched_movie_response.name == new_name, "Изменения не сохранились в базе данных"

    @allure_test_details(
        story="Попытка редактирования фильма неавторизованным пользователем",
        title="Проверка ошибки редактирования фильма без авторизации",
        description="Проверка, что неавторизованный пользователь получает ошибку 401 при попытке отредактировать фильм.",
        severity=allure.severity_level.NORMAL,
    )
    def test_edit_movie_unauthorized(self, api_manager, created_movie):
        movie_id = created_movie.id
        with allure.step(f"Попытка редактирования фильма с ID {movie_id} без токена авторизации"):
            update_payload = {"name": "Новое имя"}
            response = api_manager.movies_api.edit_movie(
                movie_id=movie_id,
                update_payload=update_payload,
                expected_status=401,
            )
        with allure.step("Проверка ответа"):
            assert isinstance(response, ErrorResponse), f"Ожидался объект ErrorResponse, но получен {type(response)}"
            assert response.status_code == 401

    @allure_test_details(
        story="Попытка редактирования несуществующего фильма",
        title="Проверка ошибки редактирования фильма с несуществующим ID",
        description="Проверка, что система возвращает ошибку 404 Not Found при попытке отредактировать фильм с ID, которого нет в базе.",
        severity=allure.severity_level.NORMAL,
    )
    def test_edit_non_existent_movie(self, admin_api_manager):
        movie_id = NON_EXISTENT_ID
        with allure.step(f"Попытка редактирования фильма с несуществующим ID: {movie_id}"):
            update_payload = {"name": "Неважно"}
            response = admin_api_manager.movies_api.edit_movie(
                movie_id=movie_id, update_payload=update_payload, expected_status=404
            )
        with allure.step("Проверка ответа об ошибке 'не найден'"):
            assert isinstance(response, ErrorResponse), f"Ожидался объект ErrorResponse, но получен {type(response)}"
            assert "не найден" in response.message_text

    @allure_test_details(
        story="Попытка редактирования фильма с невалидными данными",
        title="Проверка редактирования фильма с невалидными типами данных в полях",
        description="Проверка, что система возвращает ошибку 400 Bad Request при отправке неверных типов данных в полях.",
        severity=allure.severity_level.NORMAL,
    )
    @pytest.mark.parametrize(
        "invalid_update_payload",
        [{"price": "дорого"}, {"location": "PARIS"}, {"genreId": "боевик"}, {"name": 12345}],
    )
    def test_edit_movie_with_invalid_data(self, admin_api_manager, created_movie, invalid_update_payload):
        field_name = next(iter(invalid_update_payload))
        allure.dynamic.title(f"Редактирование с невалидным полем: '{field_name}'")
        movie_id = created_movie.id
        with allure.step(f"Попытка редактирования фильма с невалидными данными: {invalid_update_payload}"):
            response = admin_api_manager.movies_api.edit_movie(
                movie_id=movie_id, update_payload=invalid_update_payload, expected_status=400
            )
        with allure.step("Проверка, что ответ содержит ошибку 400"):
            assert isinstance(response, ErrorResponse), f"Ожидался объект ErrorResponse, но получен {type(response)}"
            assert response.status_code == 400
