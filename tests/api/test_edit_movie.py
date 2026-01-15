import logging

import allure
import pytest
import pytest_check as check

from tests.constants.endpoints import NON_EXISTENT_ID
from tests.constants.log_messages import LogMessages
from tests.models.movie_models import Movie, MovieWithReviews
from tests.models.response_models import ErrorResponse
from tests.utils.data_generator import MovieDataGenerator
from tests.utils.decorators import allure_test_details

LOGGER = logging.getLogger(__name__)


@allure.epic("Фильмы")
@allure.feature("Редактирование фильма")
class TestEditMovie:
    @allure_test_details(
        story="Успешное редактирование фильма",
        title="Тест успешного редактирования названия фильма",
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
        LOGGER.info("Запуск теста: test_edit_movie_name_success")
        movie_id = created_movie.id
        with allure.step("Подготовка: генерация нового названия для фильма"):
            new_name = "Обновленное название фильма " + MovieDataGenerator.generate_random_title(faker_instance)
            edit_payload = {"name": new_name}
            LOGGER.info(f"Подготовлены данные для редактирования фильма ID {movie_id}: новое имя - '{new_name}'")

        with allure.step(f"Отправка запроса на редактирование фильма с ID {movie_id}"):
            LOGGER.info(LogMessages.Movies.ATTEMPT_EDIT.format(movie_id))
            edited_movie_response = admin_api_manager.movies_api.edit_movie(
                movie_id=movie_id, payload=edit_payload, expected_status=200
            )

        with allure.step("Проверка данных в ответе API"):
            is_movie = isinstance(edited_movie_response, Movie)
            check.is_true(is_movie, f"Ожидался объект Movie, но получен {type(edited_movie_response)}")
            if is_movie:
                LOGGER.info(LogMessages.Movies.EDIT_SUCCESS.format(edited_movie_response.name, movie_id))
                check.equal(edited_movie_response.id, movie_id, "ID не должен меняться после редактирования")
                check.equal(edited_movie_response.name, new_name, "Название фильма должно было обновиться")
                check.equal(
                    edited_movie_response.description, created_movie.description, "Описание не должно было измениться"
                )

        with allure.step("Контрольная проверка: повторное получение фильма по ID"):
            LOGGER.info(f"Контрольная проверка: запрашиваем фильм ID {movie_id} для проверки сохранения изменений")
            fetched_movie_response = admin_api_manager.movies_api.get_movie_by_id(movie_id, expected_status=200)
            is_fetched_movie = isinstance(fetched_movie_response, MovieWithReviews)
            check.is_true(
                is_fetched_movie, f"Ожидался объект MovieWithReviews, но получен {type(fetched_movie_response)}"
            )
            if is_fetched_movie:
                LOGGER.info("Проверка в базе данных прошла успешно, название фильма совпадает с отредактированным.")
                check.equal(fetched_movie_response.name, new_name, "Изменения не сохранились в базе данных")

    @allure_test_details(
        story="Попытка редактирования фильма неавторизованным пользователем",
        title="Тест ошибки редактирования фильма без авторизации",
        description="Этот тест проверяет, что неавторизованный пользователь получает ошибку 401 при попытке отредактировать фильм.",
        severity=allure.severity_level.NORMAL,
    )
    def test_edit_movie_unauthorized(self, api_manager, created_movie):
        LOGGER.info("Запуск теста: test_edit_movie_unauthorized")
        movie_id = created_movie.id
        with allure.step(f"Попытка редактирования фильма с ID {movie_id} без токена авторизации"):
            edit_payload = {"name": "Новое имя"}
            LOGGER.info(f"Попытка редактирования фильма с ID {movie_id} без авторизации")
            response = api_manager.movies_api.edit_movie(
                movie_id=movie_id,
                payload=edit_payload,
                expected_status=401,
            )
        with allure.step("Проверка ответа"):
            is_error = isinstance(response, ErrorResponse)
            check.is_true(is_error, f"Ожидался объект ErrorResponse, но получен {type(response)}")
            if is_error:
                check.equal(response.statusCode, 401)

    @allure_test_details(
        story="Попытка редактирования несуществующего фильма",
        title="Тест ошибки редактирования фильма с несуществующим ID",
        description="Этот тест проверяет, что система возвращает ошибку 404 Not Found при попытке отредактировать фильм с ID, которого нет в базе.",
        severity=allure.severity_level.NORMAL,
    )
    def test_edit_non_existent_movie(self, admin_api_manager):
        movie_id = NON_EXISTENT_ID
        LOGGER.info(f"Запуск теста: test_edit_non_existent_movie с ID: {movie_id}")
        with allure.step(f"Попытка редактирования фильма с несуществующим ID: {movie_id}"):
            edit_payload = {"name": "Неважно"}
            LOGGER.info(LogMessages.Movies.ATTEMPT_EDIT.format(movie_id))
            response = admin_api_manager.movies_api.edit_movie(
                movie_id=movie_id, payload=edit_payload, expected_status=404
            )
        with allure.step("Проверка ответа об ошибке 'не найден'"):
            is_error = isinstance(response, ErrorResponse)
            check.is_true(is_error, f"Ожидался объект ErrorResponse, но получен {type(response)}")
            if is_error:
                LOGGER.info(f"Получена ожидаемая ошибка 404: {response.message}")
                check.is_in("не найден", response.message)

    @allure_test_details(
        story="Попытка редактирования фильма с невалидными данными",
        title="Тест редактирования фильма с невалидными типами данных в полях",
        description="Этот тест проверяет, что система возвращает ошибку 400 Bad Request при отправке неверных типов данных в полях.",
        severity=allure.severity_level.NORMAL,
    )
    @pytest.mark.parametrize(
        "invalid_data", [{"price": "дорого"}, {"location": "PARIS"}, {"genreId": "боевик"}, {"name": 12345}]
    )
    def test_edit_movie_with_invalid_data(self, admin_api_manager, created_movie, invalid_data):
        field = list(invalid_data.keys())[0]
        allure.dynamic.title(f"Тест редактирования с невалидным полем: '{field}'")
        movie_id = created_movie.id
        LOGGER.info(f"Запуск теста: test_edit_movie_with_invalid_data для ID {movie_id} с данными {invalid_data}")
        with allure.step(f"Попытка редактирования фильма с невалидными данными: {invalid_data}"):
            LOGGER.info(f"Попытка редактирования фильма ID {movie_id} с невалидными данными: {invalid_data}")
            response = admin_api_manager.movies_api.edit_movie(
                movie_id=movie_id, payload=invalid_data, expected_status=400
            )
        with allure.step("Проверка, что ответ содержит ошибку 400"):
            is_error = isinstance(response, ErrorResponse)
            check.is_true(is_error, f"Ожидался объект ErrorResponse, но получен {type(response)}")
            if is_error:
                LOGGER.info(f"Получена ожидаемая ошибка 400: {response.message}")
                check.equal(response.statusCode, 400)
