import pytest
import allure
import pytest_check as check
import logging
from tests.models.movie_models import Movie
from tests.models.response_models import ErrorResponse
from tests.utils.decorators import allure_test_details
from tests.constants.log_messages import LogMessages

LOGGER = logging.getLogger(__name__)

@allure.epic("Movies API")
@allure.feature("Создание фильма")
class TestCreateMovie:

    @allure_test_details(
        story="Успешное создание фильма",
        title="Тест создания фильма с валидными данными",
        description="""
        Проверка успешного создания нового фильма администратором.
        Шаги:
        1. Отправка POST-запроса на создание фильма с корректными данными.
        2. Проверка, что API возвращает статус 201 и данные созданного фильма.
        3. Сравнение данных в ответе с отправленными данными.
        4. Очистка: удаление созданного фильма после теста.
        """,
        severity=allure.severity_level.CRITICAL,
    )
    def test_create_movie_success(self, admin_api_manager, movie_payload):
        LOGGER.info("Запуск теста: test_create_movie_success")
        movie_id = None
        try:
            with allure.step("Отправка запроса на создание нового фильма"):
                LOGGER.info(LogMessages.Movies.ATTEMPT_CREATE.format(movie_payload.name))
                response = admin_api_manager.movies_api.create_movie(
                    movie_data=movie_payload,
                    expected_status=201
                )
                is_movie = isinstance(response, Movie)
                check.is_true(is_movie, f"Ожидался объект фильма, но получен {type(response)}")
                if is_movie:
                    created_movie = response
                    movie_id = created_movie.id
                    LOGGER.info(LogMessages.Movies.CREATE_SUCCESS.format(created_movie.name, movie_id))

                    with allure.step("Проверка данных созданного фильма в ответе"):
                        check.is_not_none(movie_id, "ID созданного фильма не должен быть пустым")
                        check.equal(created_movie.name, movie_payload.name)
                        check.equal(created_movie.description, movie_payload.description)
                        check.equal(created_movie.price, movie_payload.price)
                        check.equal(created_movie.location.value, movie_payload.location.value)
                        check.equal(created_movie.genre_id, movie_payload.genre_id)
                        check.equal(created_movie.published, movie_payload.published)

        finally:
            if movie_id:
                with allure.step("Очистка: удаление созданного фильма"):
                    LOGGER.info(f"Очистка: попытка удалить фильм с ID {movie_id}")
                    admin_api_manager.movies_api.delete_movie(movie_id, expected_status=200)
                    LOGGER.info(f"Очистка: фильм с ID {movie_id} успешно удален")

    @allure_test_details(
        story="Попытка создания фильма неавторизованным пользователем",
        title="Тест ошибки создания фильма без авторизации",
        description="Этот тест проверяет, что неавторизованный пользователь получает ошибку 401 при попытке создать фильм.",
        severity=allure.severity_level.NORMAL,
    )
    def test_create_movie_unauthorized(self, api_manager, movie_payload):
        LOGGER.info("Запуск теста: test_create_movie_unauthorized")
        with allure.step("Попытка создания фильма без токена авторизации"):
            LOGGER.info(f"Попытка создания фильма '{movie_payload.name}' без авторизации")
            response = api_manager.movies_api.create_movie(
                movie_data=movie_payload,
                expected_status=401,
            )
        with allure.step("Проверка ответа об ошибке 'Unauthorized'"):
            is_error = isinstance(response, ErrorResponse)
            check.is_true(is_error, f"Ожидался объект ErrorResponse, но получен {type(response)}")
            if is_error:
                LOGGER.info(f"Получена ожидаемая ошибка: {response.message} (Статус: {response.statusCode})")
                check.equal(response.message, "Unauthorized")
                check.equal(response.statusCode, 401)

    @allure_test_details(
        story="Попытка создания фильма с дублирующимся названием",
        title="Тест ошибки создания фильма с дублирующимся названием",
        description="Этот тест проверяет, что система возвращает ошибку 409 Conflict при попытке создать фильм с уже существующим названием.",
        severity=allure.severity_level.NORMAL,
    )
    def test_create_movie_conflict_duplicate_name(self, admin_api_manager, created_movie, movie_payload):
        LOGGER.info("Запуск теста: test_create_movie_conflict_duplicate_name")
        with allure.step("Подготовка данных: использование названия уже существующего фильма"):
            movie_payload.name = created_movie.name
        with allure.step("Попытка создания фильма с дублирующимся названием"):
            LOGGER.info(f"Попытка создания фильма с дублирующимся названием: '{movie_payload.name}'")
            response = admin_api_manager.movies_api.create_movie(
                movie_data=movie_payload,
                expected_status=409
            )
        with allure.step("Проверка ответа об ошибке 'Conflict'"):
            is_error = isinstance(response, ErrorResponse)
            check.is_true(is_error, f"Ожидался объект ErrorResponse, но получен {type(response)}")
            if is_error:
                LOGGER.info(f"Получена ожидаемая ошибка: {response.message} (Статус: {response.statusCode})")
                check.equal(response.error, "Conflict")
                check.is_in("уже существует", response.message)

    @allure_test_details(
        story="Попытка создания фильма с неполными данными",
        title="Тест ошибки создания фильма с пустым телом запроса",
        description="Этот тест проверяет, что система возвращает ошибку 400 Bad Request при отправке пустого тела запроса.",
        severity=allure.severity_level.NORMAL,
    )
    def test_create_movie_bad_request_empty_body(self, admin_api_manager):
        LOGGER.info("Запуск теста: test_create_movie_bad_request_empty_body")
        with allure.step("Отправка запроса на создание фильма с пустым телом"):
            LOGGER.info("Попытка создания фильма с пустым телом запроса")
            response = admin_api_manager.movies_api.create_movie(
                movie_data={},
                expected_status=400
            )
        with allure.step("Проверка ответа об ошибке 'Bad Request' и сообщений о валидации полей"):
            is_error = isinstance(response, ErrorResponse)
            check.is_true(is_error, f"Ожидался объект ErrorResponse, но получен {type(response)}")
            if is_error:
                LOGGER.info(f"Получена ожидаемая ошибка Bad Request с сообщениями: {response.message}")
                check.equal(response.error, "Bad Request")
                all_error_messages = " ".join(response.message)
                check.is_in("name", all_error_messages)
                check.is_in("price", all_error_messages)
                check.is_in("location", all_error_messages)

    @allure_test_details(
        story="Попытка создания фильма с невалидными типами данных",
        title="Тест создания фильма с невалидными типами данных в полях",
        description="Этот тест проверяет, что система возвращает ошибку 400 Bad Request при отправке неверных типов данных в полях.",
        severity=allure.severity_level.NORMAL,
    )
    @pytest.mark.parametrize("field_to_break, invalid_value", [
        ("name", 12345),
        ("price", "сто рублей"),
        ("location", "New York"),
        ("genreId", "первый жанр")
    ])
    def test_create_movie_bad_request_invalid_types(self, admin_api_manager, movie_payload, field_to_break, invalid_value):
        LOGGER.info(f"Запуск теста: невалидный тип для поля '{field_to_break}'")
        with allure.step(f"Подготовка невалидных данных: в поле '{field_to_break}' установлено значение '{invalid_value}'"):

            invalid_payload_dict = movie_payload.model_dump(by_alias=True)
            invalid_payload_dict[field_to_break] = invalid_value

        with allure.step("Отправка запроса на создание фильма с невалидными данными"):
            LOGGER.info(f"Попытка создания фильма с невалидным типом для поля '{field_to_break}': {invalid_value}")
            response = admin_api_manager.movies_api.create_movie(
                movie_data=invalid_payload_dict,
                expected_status=400
            )
        with allure.step("Проверка ответа об ошибке 'Bad Request'"):
            is_error = isinstance(response, ErrorResponse)
            check.is_true(is_error, f"Ожидался объект ErrorResponse, но получен {type(response)}")
            if is_error:
                LOGGER.info(f"Получена ожидаемая ошибка Bad Request с сообщением: {response.message}")
                check.equal(response.error, "Bad Request")
                check.is_true(len(response.message) > 0, "Сообщение об ошибке не должно быть пустым")

