import pytest
import allure
from tests.utils.data_generator import MovieDataGenerator
from tests.constants import NON_EXISTENT_ID

@allure.epic("Фильмы")
@allure.feature("Удаление фильма")
class TestDeleteMovie:

    @allure.story("Успешное удаление фильма")
    @allure.title("Тест успешного удаления фильма администратором")
    @allure.description("""
    Проверка полного цикла успешного удаления фильма.
    Шаги:
    1. Создание нового фильма для теста.
    2. Отправка DELETE-запроса на удаление этого фильма.
    3. Проверка, что API возвращает статус 200 и ID удаленного фильма.
    4. Проверка, что фильм действительно удален (попытка получить его по ID возвращает 404).
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.label("qa_name", "K. Koksharov")
    def test_delete_movie_success(self, admin_api_manager):
        with allure.step("Подготовка: создание нового фильма для последующего удаления"):
            payload = MovieDataGenerator.generate_valid_movie_payload()
            created_movie = admin_api_manager.movies_api.create_movie(payload, expected_status=201)
            movie_id = created_movie.id

        with allure.step(f"Отправка запроса на удаление фильма с ID: {movie_id}"):
            deleted_movie = admin_api_manager.movies_api.delete_movie(
                movie_id=movie_id,
                expected_status=200
            )
        with allure.step("Проверка, что ID в ответе совпадает с ID удаленного фильма"):
            assert deleted_movie.id == movie_id, "ID в ответе должен совпадать с ID удаленного фильма"

        with allure.step("Проверка, что фильм действительно удален (GET-запрос возвращает 404)"):
            admin_api_manager.movies_api.get_movie_by_id(
                movie_id=movie_id,
                expected_status=404
            )

    @allure.story("Попытка удаления фильма неавторизованным пользователем")
    @allure.title("Тест ошибки удаления фильма без авторизации")
    @allure.description("Этот тест проверяет, что неавторизованный пользователь получает ошибку 401 при попытке удалить фильм.")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.label("qa_name", "K. Koksharov")
    def test_delete_movie_unauthorized(self, admin_api_manager, api_manager, created_movie):
        with allure.step(f"Попытка удаления фильма с ID {created_movie.id} без токена авторизации"):
            response = api_manager.movies_api.delete_movie(
                movie_id=created_movie.id,
                expected_status=401,
            )
        with allure.step("Проверка ответа об ошибке 'Unauthorized'"):
            assert response.json()["message"] == "Unauthorized"

    @allure.story("Попытка удаления несуществующего фильма")
    @allure.title("Тест ошибки удаления фильма с несуществующим ID")
    @allure.description("Этот тест проверяет, что система возвращает ошибку 404 Not Found при попытке удалить фильм с ID, которого нет в базе.")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.label("qa_name", "K. Koksharov")
    @pytest.mark.parametrize("non_existent_id", [0, -1, NON_EXISTENT_ID])
    def test_delete_non_existent_movie(self, admin_api_manager, non_existent_id):
        with allure.step(f"Попытка удаления фильма с несуществующим ID: {non_existent_id}"):
            response = admin_api_manager.movies_api.delete_movie(
                movie_id=non_existent_id,
                expected_status=404
            )
        with allure.step("Проверка ответа об ошибке 'Фильм не найден'"):
            assert "Фильм не найден" in response.json()["message"]

    @allure.story("Попытка удаления фильма с невалидным ID")
    @allure.title("Тест ошибки удаления фильма с невалидным форматом ID")
    @allure.description("Этот тест проверяет, что система корректно обрабатывает запрос на удаление с ID неверного формата (не целое число).")
    @allure.severity(allure.severity_level.MINOR)
    @allure.label("qa_name", "K. Koksharov")
    def test_delete_movie_with_bad_request(self, admin_api_manager):
        with allure.step("Попытка удаления фильма с нецелочисленным ID ('abc')"):
            admin_api_manager.movies_api.delete_movie(
                movie_id="abc",
                expected_status=404  # Или 400, в зависимости от реализации API
            )