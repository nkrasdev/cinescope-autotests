import pytest
import allure

@allure.epic("Фильмы")
@allure.feature("Создание фильма")
class TestCreateMovie:

    @allure.story("Успешное создание фильма")
    @allure.title("Тест создания фильма с валидными данными")
    @allure.description("""
    Проверка успешного создания нового фильма администратором.
    Шаги:
    1. Отправка POST-запроса на создание фильма с корректными данными.
    2. Проверка, что API возвращает статус 201 и данные созданного фильма.
    3. Сравнение данных в ответе с отправленными данными.
    4. Очистка: удаление созданного фильма после теста.
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.label("qa_name", "K. Koksharov")
    def test_create_movie_success(self, admin_api_manager, movie_payload):
        movie_id = None
        try:
            with allure.step("Отправка запроса на создание нового фильма"):
                created_movie = admin_api_manager.movies_api.create_movie(
                    movie_data=movie_payload,
                    expected_status=201
                )
                movie_id = created_movie.id

            with allure.step("Проверка данных созданного фильма в ответе"):
                assert movie_id is not None, "ID созданного фильма не должен быть пустым"
                assert created_movie.name == movie_payload["name"]
                assert created_movie.description == movie_payload["description"]
                assert created_movie.price == movie_payload["price"]
                assert created_movie.location.value == movie_payload["location"]
                assert created_movie.genre_id == movie_payload["genreId"]
                assert created_movie.published == movie_payload["published"]

        finally:
            if movie_id:
                with allure.step("Очистка: удаление созданного фильма"):
                    admin_api_manager.movies_api.delete_movie(movie_id, expected_status=200)

    @allure.story("Попытка создания фильма неавторизованным пользователем")
    @allure.title("Тест ошибки создания фильма без авторизации")
    @allure.description("Этот тест проверяет, что неавторизованный пользователь получает ошибку 401 при попытке создать фильм.")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.label("qa_name", "K. Koksharov")
    def test_create_movie_unauthorized(self, api_manager, movie_payload):
        with allure.step("Попытка создания фильма без токена авторизации"):
            response = api_manager.movies_api.create_movie(
                movie_data=movie_payload,
                expected_status=401,
            )
        with allure.step("Проверка ответа об ошибке 'Unauthorized'"):
            response_json = response.json()
            assert response_json["message"] == "Unauthorized"
            assert response_json["statusCode"] == 401

    @allure.story("Попытка создания фильма с дублирующимся названием")
    @allure.title("Тест ошибки создания фильма с дублирующимся названием")
    @allure.description("Этот тест проверяет, что система возвращает ошибку 409 Conflict при попытке создать фильм с уже существующим названием.")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.label("qa_name", "K. Koksharov")
    def test_create_movie_conflict_duplicate_name(self, admin_api_manager, created_movie, movie_payload):
        with allure.step("Подготовка данных: использование названия уже существующего фильма"):
            movie_payload['name'] = created_movie.name
        with allure.step("Попытка создания фильма с дублирующимся названием"):
            response = admin_api_manager.movies_api.create_movie(
                movie_data=movie_payload,
                expected_status=409
            )
        with allure.step("Проверка ответа об ошибке 'Conflict'"):
            response_json = response.json()
            assert response_json.get("error") == "Conflict"
            assert "уже существует" in response_json.get("message", "")

    @allure.story("Попытка создания фильма с неполными данными")
    @allure.title("Тест ошибки создания фильма с пустым телом запроса")
    @allure.description("Этот тест проверяет, что система возвращает ошибку 400 Bad Request при отправке пустого тела запроса.")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.label("qa_name", "K. Koksharov")
    def test_create_movie_bad_request_empty_body(self, admin_api_manager):
        with allure.step("Отправка запроса на создание фильма с пустым телом"):
            response = admin_api_manager.movies_api.create_movie(
                movie_data={},
                expected_status=400
            )
        with allure.step("Проверка ответа об ошибке 'Bad Request' и сообщений о валидации полей"):
            response_json = response.json()
            assert response_json.get("error") == "Bad Request"
            all_error_messages = " ".join(response_json.get("message", []))
            assert "name" in all_error_messages
            assert "price" in all_error_messages
            assert "location" in all_error_messages

    @allure.story("Попытка создания фильма с невалидными типами данных")
    @allure.title("Тест создания фильма с невалидными типами данных в полях")
    @allure.description("Этот тест проверяет, что система возвращает ошибку 400 Bad Request при отправке неверных типов данных в полях.")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.label("qa_name", "K. Koksharov")
    @pytest.mark.parametrize("field_to_break, invalid_value", [
        ("name", 12345),
        ("price", "сто рублей"),
        ("location", "New York"),
        ("genreId", "первый жанр")
    ])
    def test_create_movie_bad_request_invalid_types(self, admin_api_manager, movie_payload, field_to_break, invalid_value):
        with allure.step(f"Подготовка невалидных данных: в поле '{field_to_break}' установлено значение '{invalid_value}'"):
            invalid_payload = movie_payload.copy()
            invalid_payload[field_to_break] = invalid_value

        with allure.step("Отправка запроса на создание фильма с невалидными данными"):
            response = admin_api_manager.movies_api.create_movie(
                movie_data=invalid_payload,
                expected_status=400
            )
        with allure.step("Проверка ответа об ошибке 'Bad Request'"):
            response_json = response.json()
            assert response_json.get("error") == "Bad Request"
            assert len(response_json.get("message", [])) > 0, "Сообщение об ошибке не должно быть пустым"

