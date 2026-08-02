import allure
import pytest

from tests.models.movie_models import Location, Movie
from tests.models.response_models import ErrorResponse, MoviesPage
from tests.utils.decorators import allure_test_details


@allure.epic("Фильмы")
@allure.feature("Получение списка фильмов")
class TestGetMovies:
    @allure_test_details(
        story="Пагинация",
        title="Проверка получения фильмов с пагинацией по умолчанию",
        description="Проверка, что при запросе без параметров API возвращает первую страницу с 10 фильмами.",
        severity=allure.severity_level.NORMAL,
    )
    @pytest.mark.smoke
    def test_get_movies_default(self, api_manager):
        with allure.step("Отправка GET-запроса без параметров"):
            response = api_manager.movies_api.get_movies()
        with allure.step(
            "Проверка, что ответ содержит список фильмов и корректные параметры пагинации по умолчанию (page=1, pageSize=10)"
        ):
            assert isinstance(response, MoviesPage), f"Ожидался объект MoviesPage, но получен {type(response)}"
            assert isinstance(response.movies, list)
            for movie in response.movies:
                assert isinstance(movie, Movie)
            assert response.page == 1
            assert response.page_size == 10

    @allure_test_details(
        story="Пагинация",
        title="Проверка получения фильмов с кастомными параметрами пагинации",
        description="Проверка, что API корректно обрабатывает параметры пагинации `page` и `pageSize`.",
        severity=allure.severity_level.NORMAL,
    )
    def test_get_movies_with_pagination(self, api_manager):
        page_size = 5
        params = {"page": 2, "pageSize": page_size}
        with allure.step(f"Отправка GET-запроса с кастомной пагинацией: {params}"):
            response = api_manager.movies_api.get_movies(params=params)

        with allure.step("Проверка, что ответ содержит список фильмов и соответствует заданным параметрам пагинации"):
            assert isinstance(response, MoviesPage), f"Ожидался объект MoviesPage, но получен {type(response)}"
            assert isinstance(response.movies, list)
            assert len(response.movies) <= page_size, f"Количество фильмов не должно превышать {page_size}"
            assert response.page == 2
            assert response.page_size == page_size

    @allure_test_details(
        story="Фильтрация",
        title="Проверка фильтрации фильмов по диапазону цен",
        description="Проверка, что фильтры `minPrice` и `maxPrice` работают корректно.",
        severity=allure.severity_level.NORMAL,
    )
    def test_get_movies_price_filter(self, api_manager):
        params = {"minPrice": 100, "maxPrice": 300}
        with allure.step(f"Отправка GET-запроса с фильтром по цене: {params}"):
            response = api_manager.movies_api.get_movies(params=params)
        assert isinstance(response, MoviesPage), f"Ожидался объект MoviesPage, но получен {type(response)}"
        with allure.step("Проверка, что цены всех полученных фильмов находятся в заданном диапазоне"):
            for movie in response.movies:
                assert 100 <= movie.price <= 300, (
                    f"Цена фильма {movie.name} ({movie.price}) выходит за диапазон 100-300"
                )

    @allure_test_details(
        story="Фильтрация",
        title="Проверка фильтрации фильмов по локации",
        description="Проверка, что фильтр по `locations` работает корректно.",
        severity=allure.severity_level.NORMAL,
    )
    def test_get_movies_location_filter(self, admin_api_manager, movie_factory, movie_payload):
        with allure.step("Подготовка: создание фильма с локацией 'MSK'"):
            movie_factory.create(movie_payload.model_copy(update={"location": Location.MSK}))

        params = {"locations": ["MSK"]}
        with allure.step(f"Отправка GET-запроса с фильтром по локации: {params}"):
            response = admin_api_manager.movies_api.get_movies(params=params)
        assert isinstance(response, MoviesPage), f"Ожидался объект MoviesPage, но получен {type(response)}"
        with allure.step("Проверка, что все полученные фильмы имеют локацию 'MSK'"):
            assert len(response.movies) > 0, "Должен найтись хотя бы один фильм с локацией MSK"
            for movie in response.movies:
                assert movie.location.value == "MSK"

    @allure_test_details(
        story="Фильтрация",
        title="Проверка фильтрации фильмов по жанру",
        description="Проверка, что фильтр по `genreId` работает корректно.",
        severity=allure.severity_level.NORMAL,
    )
    def test_get_movies_genre_filter(self, api_manager):
        params = {"genreId": 1}
        with allure.step(f"Отправка GET-запроса с фильтром по жанру: {params}"):
            response = api_manager.movies_api.get_movies(params=params)
        assert isinstance(response, MoviesPage), f"Ожидался объект MoviesPage, но получен {type(response)}"
        with allure.step("Проверка, что все полученные фильмы имеют genreId=1"):
            for movie in response.movies:
                assert movie.genre_id == 1

    @allure_test_details(
        story="Сортировка",
        title="Проверка сортировки фильмов по дате создания",
        description="Проверка, что сортировка `createdAt: desc` работает корректно.",
        severity=allure.severity_level.NORMAL,
    )
    def test_get_movies_sort_created_at(self, api_manager):
        params = {"createdAt": "desc"}
        with allure.step(f"Отправка GET-запроса с сортировкой по дате: {params}"):
            response = api_manager.movies_api.get_movies(params=params)
        assert isinstance(response, MoviesPage), f"Ожидался объект MoviesPage, но получен {type(response)}"
        with allure.step("Проверка, что фильмы отсортированы по дате создания в порядке убывания"):
            dates = [movie.created_at for movie in response.movies]
            assert dates == sorted(dates, reverse=True), "Фильмы не отсортированы по убыванию даты"

    @allure_test_details(
        story="Сортировка",
        title="Проверка сортировки фильмов по дате создания по возрастанию",
        description="Проверка, что сортировка `createdAt: asc` работает корректно.",
        severity=allure.severity_level.NORMAL,
    )
    def test_get_movies_sort_created_at_asc(self, api_manager):
        params = {"createdAt": "asc"}
        with allure.step(f"Отправка GET-запроса с сортировкой по дате: {params}"):
            response = api_manager.movies_api.get_movies(params=params)
        assert isinstance(response, MoviesPage), f"Ожидался объект MoviesPage, но получен {type(response)}"
        with allure.step("Проверка, что фильмы отсортированы по дате создания в порядке возрастания"):
            dates = [movie.created_at for movie in response.movies]
            assert dates == sorted(dates), "Фильмы не отсортированы по возрастанию даты"

    @allure_test_details(
        story="Фильтрация",
        title="Проверка получения опубликованных фильмов по умолчанию",
        description="Проверка, что по умолчанию API возвращает только опубликованные фильмы (`published: true`).",
        severity=allure.severity_level.NORMAL,
    )
    def test_get_movies_published_default(self, api_manager):
        with allure.step("Отправка GET-запроса без параметра 'published'"):
            response = api_manager.movies_api.get_movies()
        assert isinstance(response, MoviesPage), f"Ожидался объект MoviesPage, но получен {type(response)}"
        with allure.step("Проверка, что все полученные фильмы имеют статус 'published: true'"):
            for movie in response.movies:
                assert movie.published

    @allure_test_details(
        story="Фильтрация",
        title="Проверка фильтрации неопубликованных фильмов",
        description="Проверка, что при запросе с флагом 'published=false' в ответе приходят только неопубликованные фильмы.",
        severity=allure.severity_level.NORMAL,
    )
    @pytest.mark.xfail(reason="API bug: returns published movies when unpublished are requested", strict=True)
    def test_get_movies_unpublished(self, admin_api_manager):
        with allure.step("Запрос списка неопубликованных фильмов"):
            response = admin_api_manager.movies_api.get_movies(params={"published": False})
        assert isinstance(response, MoviesPage), f"Ожидался объект MoviesPage, но получен {type(response)}"
        with allure.step("Проверка, что все полученные фильмы имеют статус 'published: false'"):
            for movie in response.movies:
                assert not movie.published

    @allure_test_details(
        story="Невалидные параметры запроса",
        title="Проверка запроса с невалидным размером страницы",
        description="Проверка, что API возвращает ошибку 400 при некорректном значении `pageSize`.",
        severity=allure.severity_level.MINOR,
    )
    @pytest.mark.parametrize("params", [{"pageSize": "abc"}, {"pageSize": 0}, {"pageSize": 21}])
    def test_invalid_page_size(self, api_manager, params):
        allure.dynamic.title(f"Проверка невалидного pageSize: {params['pageSize']}")
        with allure.step(f"Отправка GET-запроса с невалидным размером страницы: {params}"):
            response = api_manager.movies_api.get_movies(params=params, expected_status=400)
        with allure.step("Проверка, что ответ содержит ошибку 400 и упоминание 'pageSize'"):
            assert isinstance(response, ErrorResponse), f"Ожидался объект ErrorResponse, но получен {type(response)}"
            assert response.status_code == 400
            assert "pageSize" in response.message_text

    @allure_test_details(
        story="Невалидные параметры запроса",
        title="Проверка запроса с невалидной локацией",
        description="Проверка, что API возвращает ошибку 400 при передаче несуществующей локации.",
        severity=allure.severity_level.MINOR,
    )
    def test_invalid_location(self, api_manager):
        params = {"locations": ["NY"]}
        with allure.step(f"Отправка GET-запроса с невалидной локацией: {params}"):
            response = api_manager.movies_api.get_movies(params=params, expected_status=400)
        with allure.step("Проверка, что ответ содержит ошибку 400 и упоминание 'locations'"):
            assert isinstance(response, ErrorResponse), f"Ожидался объект ErrorResponse, но получен {type(response)}"
            assert response.status_code == 400
            assert response.message == "Некорректные данные"

    @allure_test_details(
        story="Невалидные параметры запроса",
        title="Проверка запроса с невалидным значением сортировки",
        description="Проверка, что API возвращает ошибку 400, если в `createdAt` передано не 'asc' или 'desc'.",
        severity=allure.severity_level.MINOR,
    )
    def test_invalid_created_at_enum(self, api_manager):
        params = {"createdAt": "random"}
        with allure.step(f"Отправка GET-запроса с невалидным значением сортировки: {params}"):
            response = api_manager.movies_api.get_movies(params=params, expected_status=400)
        with allure.step("Проверка, что ответ содержит ошибку 400 и корректное сообщение"):
            assert isinstance(response, ErrorResponse), f"Ожидался объект ErrorResponse, но получен {type(response)}"
            assert response.status_code == 400
            assert response.message == "Некорректные данные"

    @allure_test_details(
        story="Невалидные параметры запроса",
        title="Проверка запроса с невалидным ID жанра",
        description="Проверка, что API возвращает ошибку 400 при некорректном значении `genreId`.",
        severity=allure.severity_level.MINOR,
    )
    def test_invalid_genre_id(self, api_manager):
        params = {"genreId": 0}
        with allure.step(f"Отправка GET-запроса с невалидным ID жанра: {params}"):
            response = api_manager.movies_api.get_movies(params=params, expected_status=400)
        with allure.step("Проверка, что ответ содержит ошибку 400 и упоминание 'genreId'"):
            assert isinstance(response, ErrorResponse), f"Ожидался объект ErrorResponse, но получен {type(response)}"
            assert response.status_code == 400
            assert "genreId" in response.message_text
