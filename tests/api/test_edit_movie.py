import pytest
import allure
from tests.utils.data_generator import MovieDataGenerator
from tests.constants import NON_EXISTENT_ID

@allure.epic("Фильмы")
@allure.feature("Редактирование фильма")
class TestEditMovie:

    @allure.story("Успешное редактирование фильма")
    @allure.title("Тест успешного редактирования названия фильма")
    @allure.description("""
    Проверка, что администратор может успешно отредактировать название существующего фильма.
    Шаги:
    1. Создание фильма через фикстуру.
    2. Генерация нового названия и отправка PATCH-запроса на редактирование.
    3. Проверка, что API возвращает статус 200 и обновленные данные фильма.
    4. Проверка, что название действительно изменилось.
    5. Повторное получение фильма по ID для подтверждения сохранения изменений в базе.
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.label("qa_name", "K. Koksharov")
    def test_edit_movie_name_success(self, admin_api_manager, created_movie):
        with allure.step("Подготовка: генерация нового названия для фильма"):
            new_name = "Обновленное название фильма " + MovieDataGenerator.generate_random_title()
            edit_payload = {"name": new_name}

        with allure.step(f"Отправка запроса на редактирование фильма с ID {created_movie.id}"):
            edited_movie = admin_api_manager.movies_api.edit_movie(
                movie_id=created_movie.id,
                payload=edit_payload,
                expected_status=200
            )

        with allure.step("Проверка данных в ответе API"):
            assert edited_movie.id == created_movie.id, "ID не должен меняться после редактирования"
            assert edited_movie.name == new_name, "Название фильма должно было обновиться"
            assert edited_movie.description == created_movie.description, "Описание не должно было измениться"

        with allure.step("Контрольная проверка: повторное получение фильма по ID"):
            fetched_movie = admin_api_manager.movies_api.get_movie_by_id(created_movie.id, expected_status=200)
            assert fetched_movie.name == new_name, "Изменения не сохранились в базе данных"

    @allure.story("Попытка редактирования фильма неавторизованным пользователем")
    @allure.title("Тест ошибки редактирования фильма без авторизации")
    @allure.description("Этот тест проверяет, что неавторизованный пользователь получает ошибку 401 при попытке отредактировать фильм.")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.label("qa_name", "K. Koksharov")
    def test_edit_movie_unauthorized(self, api_manager, created_movie):
        with allure.step(f"Попытка редактирования фильма с ID {created_movie.id} без токена авторизации"):
            edit_payload = {"name": "Новое имя"}
            response = api_manager.movies_api.edit_movie(
                movie_id=created_movie.id,
                payload=edit_payload,
                expected_status=401,
            )
        with allure.step("Проверка ответа об ошибке 'Unauthorized'"):
            assert response.json()["message"] == "Unauthorized"

    @allure.story("Попытка редактирования несуществующего фильма")
    @allure.title("Тест ошибки редактирования фильма с несуществующим ID")
    @allure.description("Этот тест проверяет, что система возвращает ошибку 404 Not Found при попытке отредактировать фильм с ID, которого нет в базе.")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.label("qa_name", "K. Koksharov")
    def test_edit_non_existent_movie(self, admin_api_manager):
        with allure.step(f"Попытка редактирования фильма с несуществующим ID: {NON_EXISTENT_ID}"):
            edit_payload = {"name": "Неважно"}
            response = admin_api_manager.movies_api.edit_movie(
                movie_id=NON_EXISTENT_ID,
                payload=edit_payload,
                expected_status=404
            )
        with allure.step("Проверка ответа об ошибке 'не найден'"):
            assert "не найден" in response.json()["message"]

    @allure.story("Попытка редактирования фильма с невалидными данными")
    @allure.title("Тест редактирования фильма с невалидными типами данных в полях")
    @allure.description("Этот тест проверяет, что система возвращает ошибку 400 Bad Request при отправке неверных типов данных в полях.")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.label("qa_name", "K. Koksharov")
    @pytest.mark.parametrize("invalid_data", [
        {"price": "дорого"},
        {"location": "PARIS"},
        {"genreId": "боевик"},
        {"name": 12345}
    ])
    def test_edit_movie_with_invalid_data(self, admin_api_manager, created_movie, invalid_data):
        with allure.step(f"Попытка редактирования фильма с невалидными данными: {invalid_data}"):
            admin_api_manager.movies_api.edit_movie(
                movie_id=created_movie.id,
                payload=invalid_data,
                expected_status=400
            )