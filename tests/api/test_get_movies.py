import pytest
import allure
from tests.models.movie import Movie

@allure.epic("Фильмы")
@allure.feature("Получение списка фильмов")
class TestGetMovies:

    @allure.story("Пагинация")
    @allure.title("Тест получения фильмов с пагинацией по умолчанию")
    @allure.description("Проверка, что при запросе без параметров API возвращает первую страницу с 10 фильмами.")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.label("qa_name", "K. Koksharov")
    def test_get_movies_default(self, api_manager):
        with allure.step("Отправка GET-запроса без параметров"):
            response = api_manager.movies_api.get_movies()
        with allure.step("Проверка, что ответ содержит список фильмов и корректные параметры пагинации по умолчанию (page=1, pageSize=10)"):
            assert isinstance(response.movies, list)
            for movie in response.movies:
                assert isinstance(movie, Movie)
            assert response.page == 1
            assert response.page_size == 10

    @allure.story("Пагинация")
    @allure.title("Тест получения фильмов с кастомными параметрами пагинации")
    @allure.description("Проверка, что API корректно обрабатывает параметры пагинации `page` и `pageSize`.")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.label("qa_name", "K. Koksharov")
    def test_get_movies_with_pagination(self, api_manager):
        page_size = 5
        params = {"page": 2, "pageSize": page_size}
        with allure.step(f"Отправка GET-запроса с кастомной пагинацией: {params}"):
            response = api_manager.movies_api.get_movies(params=params)

        with allure.step("Проверка, что ответ содержит список фильмов и соответствует заданным параметрам пагинации"):
            assert isinstance(response.movies, list)
            assert len(response.movies) <= page_size, f"Количество фильмов не должно превышать {page_size}"
            assert response.page == 2
            assert response.page_size == page_size

    @allure.story("Фильтрация")
    @allure.title("Тест фильтрации фильмов по диапазону цен")
    @allure.description("Этот тест проверяет, что фильтры `minPrice` и `maxPrice` работают корректно.")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.label("qa_name", "K. Koksharov")
    def test_get_movies_price_filter(self, api_manager):
        params = {"minPrice": 100, "maxPrice": 300}
        with allure.step(f"Отправка GET-запроса с фильтром по цене: {params}"):
            movies = api_manager.movies_api.get_movies(params=params).movies
        with allure.step("Проверка, что цены всех полученных фильмов находятся в заданном диапазоне"):
            for movie in movies:
                assert 100 <= movie.price <= 300, f"Цена фильма {movie.name} ({movie.price}) выходит за диапазон 100-300"

    @allure.story("Фильтрация")
    @allure.title("Тест фильтрации фильмов по локации")
    @allure.description("Этот тест проверяет, что фильтр по `locations` работает корректно.")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.label("qa_name", "K. Koksharov")
    def test_get_movies_location_filter(self, admin_api_manager, movie_payload):
        movie_id = None
        try:
            with allure.step("Подготовка: создание фильма с локацией 'MSK'"):
                movie_payload["location"] = "MSK"
                created_movie = admin_api_manager.movies_api.create_movie(movie_payload)
                movie_id = created_movie.id

            params = {"locations": ["MSK"]}
            with allure.step(f"Отправка GET-запроса с фильтром по локации: {params}"):
                movies = admin_api_manager.movies_api.get_movies(params=params).movies

            with allure.step("Проверка, что все полученные фильмы имеют локацию 'MSK'"):
                assert len(movies) > 0, "Должен найтись хотя бы один фильм с локацией MSK"
                for movie in movies:
                    assert movie.location.value == "MSK"
        finally:
            if movie_id:
                with allure.step(f"Очистка: удаление тестового фильма с ID {movie_id}"):
                    admin_api_manager.movies_api.delete_movie(movie_id)

    @allure.story("Фильтрация")
    @allure.title("Тест фильтрации фильмов по жанру")
    @allure.description("Этот тест проверяет, что фильтр по `genreId` работает корректно.")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.label("qa_name", "K. Koksharov")
    def test_get_movies_genre_filter(self, api_manager):
        params = {"genreId": 1}
        with allure.step(f"Отправка GET-запроса с фильтром по жанру: {params}"):
            movies = api_manager.movies_api.get_movies(params=params).movies
        with allure.step("Проверка, что все полученные фильмы имеют genreId=1"):
            for movie in movies:
                assert movie.genre_id == 1

    @allure.story("Сортировка")
    @allure.title("Тест сортировки фильмов по дате создания")
    @allure.description("Этот тест проверяет, что сортировка `createdAt: desc` работает корректно.")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.label("qa_name", "K. Koksharov")
    def test_get_movies_sort_created_at(self, api_manager):
        params = {"createdAt": "desc"}
        with allure.step(f"Отправка GET-запроса с сортировкой по дате: {params}"):
            movies = api_manager.movies_api.get_movies(params=params).movies
        with allure.step("Проверка, что фильмы отсортированы по дате создания в порядке убывания"):
            dates = [movie.created_at for movie in movies]
            assert dates == sorted(dates, reverse=True), "Фильмы не отсортированы по убыванию даты"

    @allure.story("Фильтрация")
    @allure.title("Тест получения опубликованных фильмов по умолчанию")
    @allure.description("Этот тест проверяет, что по умолчанию API возвращает только опубликованные фильмы (`published: true`).")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.label("qa_name", "K. Koksharov")
    def test_get_movies_published_default(self, api_manager):
        with allure.step("Отправка GET-запроса без параметра 'published'"):
            movies = api_manager.movies_api.get_movies().movies
        with allure.step("Проверка, что все полученные фильмы имеют статус 'published: true'"):
            for movie in movies:
                assert movie.published is True

    @allure.story("Фильтрация")
    @allure.title("Тест фильтрации неопубликованных фильмов")
    @allure.description("Этот тест проверяет, что фильтр `published: false` работает корректно.")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.label("qa_name", "K. Koksharov")
    def test_get_movies_unpublished(self, api_manager):
        params = {"published": False}
        with allure.step("Отправка GET-запроса с параметром 'published: false'"):
            movies = api_manager.movies_api.get_movies(params=params).movies
        with allure.step("Проверка, что все полученные фильмы имеют статус 'published: false'"):
            for movie in movies:
                assert movie.published is False

    @allure.story("Невалидные параметры запроса")
    @allure.title("Тест запроса с невалидным размером страницы")
    @allure.description("Этот тест проверяет, что API возвращает ошибку 400 при некорректном значении `pageSize`.")
    @allure.severity(allure.severity_level.MINOR)
    @allure.label("qa_name", "K. Koksharov")
    @pytest.mark.parametrize("params", [
        {"pageSize": "abc"},
        {"pageSize": 0},
        {"pageSize": 21}
    ])
    def test_invalid_page_size(self, api_manager, params):
        with allure.step(f"Отправка GET-запроса с невалидным размером страницы: {params}"):
            response = api_manager.movies_api.get_movies_with_invalid_params(
                params=params,
                expected_status=400
            )
        with allure.step("Проверка, что ответ содержит ошибку 400 и упоминание 'pageSize'"):
            assert response.status_code == 400
            assert "pageSize" in str(response.json())

    @allure.story("Невалидные параметры запроса")
    @allure.title("Тест запроса с невалидной локацией")
    @allure.description("Этот тест проверяет, что API возвращает ошибку 400 при передаче несуществующей локации.")
    @allure.severity(allure.severity_level.MINOR)
    @allure.label("qa_name", "K. Koksharov")
    def test_invalid_location(self, api_manager):
        params = {"locations": ["NY"]}
        with allure.step(f"Отправка GET-запроса с невалидной локацией: {params}"):
            response = api_manager.movies_api.get_movies_with_invalid_params(
                params=params,
                expected_status=400
            )
        with allure.step("Проверка, что ответ содержит ошибку 400 и упоминание 'locations'"):
            assert response.status_code == 400
            assert "locations" in str(response.json())

    @allure.story("Невалидные параметры запроса")
    @allure.title("Тест запроса с невалидным значением сортировки")
    @allure.description("Этот тест проверяет, что API возвращает ошибку 400, если в `createdAt` передано не 'asc' или 'desc'.")
    @allure.severity(allure.severity_level.MINOR)
    @allure.label("qa_name", "K. Koksharov")
    def test_invalid_created_at_enum(self, api_manager):
        params = {"createdAt": "random"}
        with allure.step(f"Отправка GET-запроса с невалидным значением сортировки: {params}"):
            response = api_manager.movies_api.get_movies_with_invalid_params(
                params=params,
                expected_status=400
            )
        with allure.step("Проверка, что ответ содержит ошибку 400 и корректное сообщение"):
            assert response.status_code == 400
            response_json = response.json()
            assert "message" in response_json
            assert response_json["message"] == "Некорректные данные"

    @allure.story("Невалидные параметры запроса")
    @allure.title("Тест запроса с невалидным ID жанра")
    @allure.description("Этот тест проверяет, что API возвращает ошибку 400 при некорректном значении `genreId`.")
    @allure.severity(allure.severity_level.MINOR)
    @allure.label("qa_name", "K. Koksharov")
    def test_invalid_genre_id(self, api_manager):
        params = {"genreId": 0}
        with allure.step(f"Отправка GET-запроса с невалидным ID жанра: {params}"):
            response = api_manager.movies_api.get_movies_with_invalid_params(
                params=params,
                expected_status=400
            )
        with allure.step("Проверка, что ответ содержит ошибку 400 и упоминание 'genreId'"):
            assert response.status_code == 400
            assert "genreId" in str(response.json())
