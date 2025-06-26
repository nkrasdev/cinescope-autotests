import pytest
import allure
from tests.constants import NON_EXISTENT_ID

@allure.epic("Фильмы")
@allure.feature("Получение фильма по ID")
class TestGetMovieById:

    @allure.story("Успешное получение фильма по ID")
    @allure.title("Тест успешного получения существующего фильма по его ID")
    @allure.description("""
    Проверка, что можно успешно получить данные существующего фильма по его ID.
    Шаги:
    1. Создание фильма через фикстуру.
    2. Отправка GET-запроса с ID созданного фильма.
    3. Проверка, что API возвращает статус 200 и корректные данные фильма.
    4. Сравнение всех полей полученного фильма с данными изначального.
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.label("qa_name", "K. Koksharov")
    def test_get_existing_movie_by_id(self, admin_api_manager, created_movie):
        with allure.step(f"Отправка запроса на получение фильма с ID: {created_movie.id}"):
            movie_id = created_movie.id
            fetched_movie = admin_api_manager.movies_api.get_movie_by_id(movie_id, expected_status=200)

        with allure.step("Проверка, что данные полученного фильма соответствуют ожидаемым"):
            assert fetched_movie.id == created_movie.id
            assert fetched_movie.name == created_movie.name
            assert fetched_movie.description == created_movie.description
            assert fetched_movie.price == created_movie.price
            assert fetched_movie.location == created_movie.location
            assert fetched_movie.genre_id == created_movie.genre_id
            assert fetched_movie.published == created_movie.published
            assert fetched_movie.reviews == [], "У нового фильма не должно быть отзывов"

    @allure.story("Попытка получения несуществующего фильма")
    @allure.title("Тест ошибки получения фильма с несуществующим ID")
    @allure.description("Этот тест проверяет, что система возвращает ошибку 404 Not Found при запросе фильма с ID, которого нет в базе.")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.label("qa_name", "K. Koksharov")
    def test_get_movie_not_found(self, admin_api_manager):
        with allure.step(f"Попытка получения фильма с несуществующим ID: {NON_EXISTENT_ID}"):
            response = admin_api_manager.movies_api.get_movie_by_id(NON_EXISTENT_ID, expected_status=404)
        with allure.step("Проверка ответа об ошибке 'Фильм не найден'"):
            response_json = response.json()
            assert response.status_code == 404
            assert response_json["statusCode"] == 404
            assert response_json["message"] == "Фильм не найден"

    @allure.story("Попытка получения несуществующего фильма")
    @allure.title("Тест ошибки получения фильма с невалидным (отрицательным или 0) ID")
    @allure.description("Этот тест проверяет, что система возвращает ошибку 404 Not Found при запросе фильма с ID <= 0.")
    @allure.severity(allure.severity_level.MINOR)
    @allure.label("qa_name", "K. Koksharov")
    @pytest.mark.parametrize("invalid_id", [0, -1])
    def test_get_movie_not_found_invalid_id(self, admin_api_manager, invalid_id):
        with allure.step(f"Попытка получения фильма с невалидным ID: {invalid_id}"):
            admin_api_manager.movies_api.get_movie_by_id(
                invalid_id,
                expected_status=404
            )

    @allure.story("Попытка получения фильма с невалидным форматом ID")
    @allure.title("Тест ошибки получения фильма с нецелочисленным форматом ID")
    @allure.description("Этот тест проверяет, что система возвращает ошибку 500 (или 400) при запросе фильма с ID неверного формата (не целое число).")
    @allure.severity(allure.severity_level.MINOR)
    @allure.label("qa_name", "K. Koksharov")
    def test_get_movie_bad_request(self, admin_api_manager):
        with allure.step("Попытка получения фильма со строковым ID ('abc')"):
            admin_api_manager.movies_api.get_movie_by_id(
                "abc",
                expected_status=500  # Или 400, в зависимости от реализации API
            )
