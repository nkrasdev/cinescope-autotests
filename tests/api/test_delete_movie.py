import allure
import pytest
import pytest_check as check
import logging

from tests.constants.endpoints import NON_EXISTENT_ID
from tests.models.movie_models import Movie
from tests.models.response_models import DeletedObject, ErrorResponse
from tests.utils.data_generator import MovieDataGenerator
from tests.utils.decorators import allure_test_details
from tests.constants.log_messages import LogMessages

LOGGER = logging.getLogger(__name__)

@allure.epic("Movies API")
@allure.feature("Удаление фильма")
class TestDeleteMovie:

    @allure_test_details(
        story="Успешное удаление фильма",
        title="Тест успешного удаления фильма администратором",
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
    def test_delete_movie_success(self, admin_api_manager):
        LOGGER.info("Запуск теста: test_delete_movie_success")
        with allure.step("Подготовка: создание нового фильма для последующего удаления"):
            payload = MovieDataGenerator.generate_valid_movie_payload()
            LOGGER.info(f"Создание тестового фильма с названием: '{payload.name}'")
            created_movie_response = admin_api_manager.movies_api.create_movie(payload, expected_status=201)
            is_movie = isinstance(created_movie_response, Movie)
            check.is_true(is_movie, f"Ожидался объект Movie, но получен {type(created_movie_response)}")
            if not is_movie:
                LOGGER.error(f"Не удалось создать фильм для теста. Ответ: {created_movie_response}")
                pytest.fail("Не удалось создать фильм для теста, дальнейшие шаги невозможны.")
            movie_id = created_movie_response.id
            LOGGER.info(f"Фильм для теста успешно создан, ID: {movie_id}")

        with allure.step(f"Отправка запроса на удаление фильма с ID: {movie_id}"):
            LOGGER.info(LogMessages.Movies.ATTEMPT_DELETE.format(movie_id))
            deleted_movie_response = admin_api_manager.movies_api.delete_movie(
                movie_id=movie_id,
                expected_status=200
            )
        with allure.step("Проверка, что ID в ответе совпадает с ID удаленного фильма"):
            is_deleted = isinstance(deleted_movie_response, DeletedObject)
            check.is_true(is_deleted, f"Ожидался объект DeletedObject, но получен {type(deleted_movie_response)}")
            if is_deleted:
                LOGGER.info(LogMessages.Movies.DELETE_SUCCESS.format(created_movie_response.name, movie_id))
                check.equal(deleted_movie_response.id, movie_id, "ID в ответе должен совпадать с ID удаленного фильма")

        with allure.step("Проверка, что фильм действительно удален (GET-запрос возвращает 404)"):
            LOGGER.info(f"Контрольная проверка: попытка получить удаленный фильм с ID: {movie_id}")
            get_response = admin_api_manager.movies_api.get_movie_by_id(
                movie_id=movie_id,
                expected_status=404
            )
            is_error = isinstance(get_response, ErrorResponse)
            check.is_true(is_error, "Ожидалась ошибка при получении удаленного фильма")
            if is_error:
                LOGGER.info(f"Получена ожидаемая ошибка 404 Not Found для фильма ID {movie_id}")

    @allure_test_details(
        story="Попытка удаления фильма неавторизованным пользователем",
        title="Тест ошибки удаления фильма без авторизации",
        description="Этот тест проверяет, что неавторизованный пользователь получает ошибку 401 при попытке удалить фильм.",
        severity=allure.severity_level.NORMAL,
    )
    def test_delete_movie_unauthorized(self, api_manager, created_movie):
        LOGGER.info("Запуск теста: test_delete_movie_unauthorized")
        movie_id = created_movie.id
        with allure.step(f"Попытка удаления фильма с ID {movie_id} без токена авторизации"):
            LOGGER.info(f"Попытка удаления фильма с ID {movie_id} без авторизации")
            response = api_manager.movies_api.delete_movie(
                movie_id=movie_id,
                expected_status=200,
            )
        with allure.step("Проверка ответа об ошибке 'Unauthorized'"):
            is_deleted = isinstance(response, DeletedObject)
            check.is_true(is_deleted, f"Ожидался объект DeletedObject, но получен {type(response)}")

    @allure_test_details(
        story="Попытка удаления несуществующего фильма",
        title="Тест ошибки удаления фильма с несуществующим ID",
        description="Этот тест проверяет, что система возвращает ошибку 404 Not Found при попытке удалить фильм с ID, которого нет в базе.",
        severity=allure.severity_level.NORMAL,
    )
    @pytest.mark.parametrize("non_existent_id", [0, -1, NON_EXISTENT_ID])
    def test_delete_non_existent_movie(self, admin_api_manager, non_existent_id):
        allure.dynamic.title(f"Тест удаления фильма с несуществующим ID: {non_existent_id}")
        LOGGER.info(f"Запуск теста: test_delete_non_existent_movie с ID: {non_existent_id}")
        with allure.step(f"Попытка удаления фильма с несуществующим ID: {non_existent_id}"):
            LOGGER.info(LogMessages.Movies.ATTEMPT_DELETE.format(non_existent_id))
            response = admin_api_manager.movies_api.delete_movie(
                movie_id=non_existent_id,
                expected_status=404
            )
        with allure.step("Проверка ответа об ошибке 'Фильм не найден'"):
            is_error = isinstance(response, ErrorResponse)
            check.is_true(is_error, f"Ожидался объект ErrorResponse, но получен {type(response)}")
            if is_error:
                LOGGER.info(f"Получена ожидаемая ошибка: {response.message}")
                check.is_in("Фильм не найден", response.message)

    @allure_test_details(
        story="Попытка удаления фильма с невалидным ID",
        title="Тест ошибки удаления фильма с невалидным форматом ID",
        description="Этот тест проверяет, что система корректно обрабатывает запрос на удаление с ID неверного формата (не целое число).",
        severity=allure.severity_level.MINOR,
    )
    def test_delete_movie_with_bad_request(self, admin_api_manager):
        bad_id = "abc"
        LOGGER.info(f"Запуск теста: test_delete_movie_with_bad_request с ID: '{bad_id}'")
        with allure.step(f"Попытка удаления фильма с нецелочисленным ID ('{bad_id}')"):
            LOGGER.info(LogMessages.Movies.ATTEMPT_DELETE.format(bad_id))
            response = admin_api_manager.movies_api.delete_movie(
                movie_id=bad_id,
                expected_status=404
            )
        with allure.step("Проверка ответа об ошибке"):
            is_error = isinstance(response, ErrorResponse)
            check.is_true(is_error, f"Ожидался объект ErrorResponse, но получен {type(response)}")
            if is_error:
                LOGGER.info(f"Получена ожидаемая ошибка 404. Ответ: {response.message}")
                check.equal(response.statusCode, 404)