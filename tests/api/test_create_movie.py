import allure
import pytest

from tests.models.response_models import ErrorResponse
from tests.utils.data_generator import MovieDataGenerator
from tests.utils.decorators import allure_test_details


@allure.epic("Фильмы")
@allure.feature("Создание фильма")
class TestCreateMovie:
    @allure_test_details(
        story="Успешное создание фильма",
        title="Проверка создания фильма с валидными данными",
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
    def test_create_movie_success(self, movie_factory, movie_payload):
        with allure.step("Отправка запроса на создание нового фильма"):
            created_movie = movie_factory.create(movie_payload)

        with allure.step("Проверка данных созданного фильма в ответе"):
            assert created_movie.id is not None, "ID созданного фильма не должен быть пустым"
            assert created_movie.name == movie_payload.name
            assert created_movie.description == movie_payload.description
            assert created_movie.price == movie_payload.price
            assert created_movie.location.value == movie_payload.location.value
            assert created_movie.genre_id == movie_payload.genre_id
            assert created_movie.published == movie_payload.published

    @allure_test_details(
        story="Попытка создания фильма неавторизованным пользователем",
        title="Проверка ошибки создания фильма без авторизации",
        description="Проверка, что неавторизованный пользователь получает ошибку 401 при попытке создать фильм.",
        severity=allure.severity_level.NORMAL,
    )
    def test_create_movie_unauthorized(self, api_manager, movie_payload):
        with allure.step("Попытка создания фильма без токена авторизации"):
            response = api_manager.movies_api.create_movie(
                movie_data=movie_payload,
                expected_status=401,
            )
        with allure.step("Проверка ответа об ошибке 'Unauthorized'"):
            assert isinstance(response, ErrorResponse), f"Ожидался объект ErrorResponse, но получен {type(response)}"
            assert response.message == "Unauthorized"
            assert response.status_code == 401

    @allure_test_details(
        story="Попытка создания фильма с дублирующимся названием",
        title="Проверка ошибки создания фильма с дублирующимся названием",
        description="Проверка, что система возвращает ошибку 409 Conflict при попытке создать фильм с уже существующим названием.",
        severity=allure.severity_level.NORMAL,
    )
    def test_create_movie_conflict_duplicate_name(self, admin_api_manager, created_movie, movie_payload):
        with allure.step("Подготовка данных: использование названия уже существующего фильма"):
            movie_payload.name = created_movie.name
        with allure.step("Попытка создания фильма с дублирующимся названием"):
            response = admin_api_manager.movies_api.create_movie(movie_data=movie_payload, expected_status=409)
        with allure.step("Проверка ответа об ошибке 'Conflict'"):
            assert isinstance(response, ErrorResponse), f"Ожидался объект ErrorResponse, но получен {type(response)}"
            assert response.error == "Conflict"
            assert "уже существует" in response.message

    @allure_test_details(
        story="Попытка создания фильма с неполными данными",
        title="Проверка ошибки создания фильма с пустым телом запроса",
        description="Проверка, что система возвращает ошибку 400 Bad Request при отправке пустого тела запроса.",
        severity=allure.severity_level.NORMAL,
    )
    def test_create_movie_bad_request_empty_body(self, admin_api_manager):
        with allure.step("Отправка запроса на создание фильма с пустым телом"):
            response = admin_api_manager.movies_api.create_movie(movie_data={}, expected_status=400)
        with allure.step("Проверка ответа об ошибке 'Bad Request' и сообщений о валидации полей"):
            assert isinstance(response, ErrorResponse), f"Ожидался объект ErrorResponse, но получен {type(response)}"
            assert response.error == "Bad Request"
            all_error_messages = response.message_text
            assert "name" in all_error_messages
            assert "price" in all_error_messages
            assert "location" in all_error_messages

    @allure_test_details(
        story="Попытка создания фильма с неполными данными",
        title="Проверка ошибки создания фильма с отсутствующим обязательным полем",
        description="Проверка, что система возвращает ошибку 400 при отсутствии обязательного поля.",
        severity=allure.severity_level.NORMAL,
    )
    @pytest.mark.parametrize("missing_field", ["name", "description", "price", "location", "genreId"])
    def test_create_movie_bad_request_missing_field(self, admin_api_manager, faker_instance, missing_field):
        allure.dynamic.title(f"Проверка создания фильма без обязательного поля: '{missing_field}'")
        with allure.step(f"Подготовка данных без поля '{missing_field}'"):
            invalid_payload_dict = MovieDataGenerator.generate_movie_payload_missing_field(
                faker_instance, missing_field
            )

        with allure.step("Отправка запроса на создание фильма с отсутствующим полем"):
            response = admin_api_manager.movies_api.create_movie(movie_data=invalid_payload_dict, expected_status=400)
        with allure.step("Проверка ответа об ошибке 'Bad Request'"):
            assert isinstance(response, ErrorResponse), f"Ожидался объект ErrorResponse, но получен {type(response)}"
            assert response.error == "Bad Request"
            assert response.status_code == 400
            assert bool(response.message_text), "Сообщение об ошибке не должно быть пустым"

    @allure_test_details(
        story="Попытка создания фильма с невалидными типами данных",
        title="Проверка создания фильма с невалидными типами данных в полях",
        description="Проверка, что система возвращает ошибку 400 Bad Request при отправке неверных типов данных в полях.",
        severity=allure.severity_level.NORMAL,
    )
    @pytest.mark.parametrize(
        "field_to_break, invalid_value",
        [("name", 12345), ("price", "сто рублей"), ("location", "New York"), ("genreId", "первый жанр")],
    )
    def test_create_movie_bad_request_invalid_types(
        self, admin_api_manager, faker_instance, field_to_break, invalid_value
    ):
        allure.dynamic.title(f"Проверка создания фильма с невалидным полем: '{field_to_break}'")
        with allure.step(
            f"Подготовка невалидных данных: в поле '{field_to_break}' установлено значение '{invalid_value}'"
        ):
            invalid_payload_dict = MovieDataGenerator.generate_movie_payload_with_invalid_field(
                faker_instance, field_to_break, invalid_value
            )

        with allure.step("Отправка запроса на создание фильма с невалидными данными"):
            response = admin_api_manager.movies_api.create_movie(movie_data=invalid_payload_dict, expected_status=400)
        with allure.step("Проверка ответа об ошибке 'Bad Request'"):
            assert isinstance(response, ErrorResponse), f"Ожидался объект ErrorResponse, но получен {type(response)}"
            assert response.error == "Bad Request"
            assert bool(response.message_text), "Сообщение об ошибке не должно быть пустым"
