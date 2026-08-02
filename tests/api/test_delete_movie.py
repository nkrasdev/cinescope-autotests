import allure
import pytest

from tests.constants.endpoints import NON_EXISTENT_ID
from tests.models.response_models import DeletedResource, ErrorResponse
from tests.utils.decorators import allure_test_details


@allure.epic("Фильмы")
@allure.feature("Удаление фильма")
class TestDeleteMovie:
    @allure_test_details(
        story="Успешное удаление фильма",
        title="Проверка успешного удаления фильма администратором",
        description="""
        Проверка полного цикла успешного удаления фильма.
        Шаги:
        1. Создание нового фильма для теста.
        2. Отправка DELETE-запроса на удаление этого фильма.
        3. Проверка, что API возвращает статус 200 и ID удаленного фильма.
        4. Проверка, что фильм действительно удален (попытка получить его по ID возвращает 404).
        """,
        severity=allure.severity_level.CRITICAL,
    )
    def test_delete_movie_success(self, admin_api_manager, created_movie, movie_factory):
        movie_id = created_movie.id

        with allure.step(f"Отправка запроса на удаление фильма с ID: {movie_id}"):
            deleted_movie_response = admin_api_manager.movies_api.delete_movie(movie_id=movie_id, expected_status=200)
        with allure.step("Проверка, что ID в ответе совпадает с ID удаленного фильма"):
            assert isinstance(deleted_movie_response, DeletedResource), (
                f"Ожидался объект DeletedResource, но получен {type(deleted_movie_response)}"
            )
            assert deleted_movie_response.id == movie_id, "ID в ответе должен совпадать с ID удаленного фильма"
            movie_factory.mark_deleted(movie_id)

        with allure.step("Проверка, что фильм действительно удален (GET-запрос возвращает 404)"):
            get_response = admin_api_manager.movies_api.get_movie_by_id(movie_id=movie_id, expected_status=404)
            assert isinstance(get_response, ErrorResponse), "Ожидалась ошибка при получении удаленного фильма"
            assert get_response.status_code == 404

    @allure_test_details(
        story="Попытка удаления фильма неавторизованным пользователем",
        title="Проверка ошибки удаления фильма без авторизации",
        description="Проверка, что неавторизованный пользователь получает ошибку 401 при попытке удалить фильм.",
        severity=allure.severity_level.NORMAL,
    )
    def test_delete_movie_unauthorized(self, api_manager, created_movie):
        movie_id = created_movie.id
        with allure.step(f"Попытка удаления фильма с ID {movie_id} без токена авторизации"):
            response = api_manager.movies_api.delete_movie(
                movie_id=movie_id,
                expected_status=401,
            )
        with allure.step("Проверка ответа об ошибке 'Unauthorized'"):
            assert isinstance(response, ErrorResponse), f"Ожидался объект ErrorResponse, но получен {type(response)}"
            assert response.status_code == 401

    @allure_test_details(
        story="Попытка удаления несуществующего фильма",
        title="Проверка ошибки удаления фильма с несуществующим ID",
        description="Проверка, что система возвращает ошибку 404 Not Found при попытке удалить фильм с ID, которого нет в базе.",
        severity=allure.severity_level.NORMAL,
    )
    @pytest.mark.parametrize("non_existent_id", [0, -1, NON_EXISTENT_ID])
    def test_delete_non_existent_movie(self, admin_api_manager, non_existent_id):
        allure.dynamic.title(f"Проверка удаления фильма с несуществующим ID: {non_existent_id}")
        with allure.step(f"Попытка удаления фильма с несуществующим ID: {non_existent_id}"):
            response = admin_api_manager.movies_api.delete_movie(movie_id=non_existent_id, expected_status=404)
        with allure.step("Проверка ответа об ошибке 'Фильм не найден'"):
            assert isinstance(response, ErrorResponse), f"Ожидался объект ErrorResponse, но получен {type(response)}"
            assert "Фильм не найден" in response.message_text

    @allure_test_details(
        story="Попытка удаления фильма с невалидным ID",
        title="Проверка ошибки удаления фильма с невалидным форматом ID",
        description="Проверка, что система корректно обрабатывает запрос на удаление с ID неверного формата (не целое число).",
        severity=allure.severity_level.MINOR,
    )
    def test_delete_movie_with_bad_request(self, admin_api_manager):
        bad_id = "abc"
        with allure.step(f"Попытка удаления фильма с нецелочисленным ID ('{bad_id}')"):
            response = admin_api_manager.movies_api.delete_movie(movie_id=bad_id, expected_status=404)
        with allure.step("Проверка ответа об ошибке"):
            assert isinstance(response, ErrorResponse), f"Ожидался объект ErrorResponse, но получен {type(response)}"
            assert response.status_code == 404
