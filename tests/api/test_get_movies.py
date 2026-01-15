import logging

import allure
import pytest
import pytest_check as check

from tests.constants.log_messages import LogMessages
from tests.models.movie_models import Location, Movie
from tests.models.response_models import ErrorResponse, MoviesList
from tests.utils.decorators import allure_test_details

LOGGER = logging.getLogger(__name__)


@allure.epic("Фильмы")
@allure.feature("Получение списка фильмов")
class TestGetMovies:
    @allure_test_details(
        story="Пагинация",
        title="Тест получения фильмов с пагинацией по умолчанию",
        description="Проверка, что при запросе без параметров API возвращает первую страницу с 10 фильмами.",
        severity=allure.severity_level.NORMAL,
    )
    def test_get_movies_default(self, api_manager):
        LOGGER.info("Запуск теста: test_get_movies_default")
        with allure.step("Отправка GET-запроса без параметров"):
            LOGGER.info(LogMessages.Movies.ATTEMPT_GET_LIST.format("default"))
            response = api_manager.movies_api.get_movies()
        with allure.step(
            "Проверка, что ответ содержит список фильмов и корректные параметры пагинации по умолчанию (page=1, pageSize=10)"
        ):
            is_list = isinstance(response, MoviesList)
            check.is_true(is_list, f"Ожидался объект MoviesList, но получен {type(response)}")
            if is_list:
                check.is_instance(response.movies, list)
                for movie in response.movies:
                    check.is_instance(movie, Movie)
                check.equal(response.page, 1)
                check.equal(response.page_size, 10)

    @allure_test_details(
        story="Пагинация",
        title="Тест получения фильмов с кастомными параметрами пагинации",
        description="Проверка, что API корректно обрабатывает параметры пагинации `page` и `pageSize`.",
        severity=allure.severity_level.NORMAL,
    )
    def test_get_movies_with_pagination(self, api_manager):
        page_size = 5
        params = {"page": 2, "pageSize": page_size}
        LOGGER.info(f"Запуск теста: test_get_movies_with_pagination с параметрами {params}")
        with allure.step(f"Отправка GET-запроса с кастомной пагинацией: {params}"):
            LOGGER.info(LogMessages.Movies.ATTEMPT_GET_LIST.format(params))
            response = api_manager.movies_api.get_movies(params=params)

        with allure.step("Проверка, что ответ содержит список фильмов и соответствует заданным параметрам пагинации"):
            is_list = isinstance(response, MoviesList)
            check.is_true(is_list, f"Ожидался объект MoviesList, но получен {type(response)}")
            if is_list:
                check.is_instance(response.movies, list)
                check.is_true(len(response.movies) <= page_size, f"Количество фильмов не должно превышать {page_size}")
                check.equal(response.page, 2)
                check.equal(response.page_size, page_size)

    @allure_test_details(
        story="Фильтрация",
        title="Тест фильтрации фильмов по диапазону цен",
        description="Этот тест проверяет, что фильтры `minPrice` и `maxPrice` работают корректно.",
        severity=allure.severity_level.NORMAL,
    )
    def test_get_movies_price_filter(self, api_manager):
        params = {"minPrice": 100, "maxPrice": 300}
        LOGGER.info(f"Запуск теста: test_get_movies_price_filter с параметрами {params}")
        with allure.step(f"Отправка GET-запроса с фильтром по цене: {params}"):
            LOGGER.info(LogMessages.Movies.ATTEMPT_GET_LIST.format(params))
            response = api_manager.movies_api.get_movies(params=params)
        is_list = isinstance(response, MoviesList)
        check.is_true(is_list, f"Ожидался объект MoviesList, но получен {type(response)}")
        if is_list:
            with allure.step("Проверка, что цены всех полученных фильмов находятся в заданном диапазоне"):
                for movie in response.movies:
                    check.is_true(
                        100 <= movie.price <= 300,
                        f"Цена фильма {movie.name} ({movie.price}) выходит за диапазон 100-300",
                    )

    @allure_test_details(
        story="Фильтрация",
        title="Тест фильтрации фильмов по локации",
        description="Этот тест проверяет, что фильтр по `locations` работает корректно.",
        severity=allure.severity_level.NORMAL,
    )
    def test_get_movies_location_filter(self, admin_api_manager, movie_payload):
        LOGGER.info("Запуск теста: test_get_movies_location_filter")
        movie_id = None
        try:
            with allure.step("Подготовка: создание фильма с локацией 'MSK'"):
                movie_payload.location = Location.MSK
                created_movie_response = admin_api_manager.movies_api.create_movie(movie_payload)
                is_movie = isinstance(created_movie_response, Movie)
                check.is_true(is_movie, f"Ожидался объект Movie, но получен {type(created_movie_response)}")
                if not is_movie:
                    pytest.fail("Не удалось создать фильм для теста.")
                movie_id = created_movie_response.id

            params = {"locations": ["MSK"]}
            with allure.step(f"Отправка GET-запроса с фильтром по локации: {params}"):
                LOGGER.info(LogMessages.Movies.ATTEMPT_GET_LIST.format(params))
                response = admin_api_manager.movies_api.get_movies(params=params)
            is_list = isinstance(response, MoviesList)
            check.is_true(is_list, f"Ожидался объект MoviesList, но получен {type(response)}")
            if is_list:
                with allure.step("Проверка, что все полученные фильмы имеют локацию 'MSK'"):
                    check.is_true(len(response.movies) > 0, "Должен найтись хотя бы один фильм с локацией MSK")
                    for movie in response.movies:
                        check.equal(movie.location.value, "MSK")
        finally:
            if movie_id:
                with allure.step(f"Очистка: удаление тестового фильма с ID {movie_id}"):
                    admin_api_manager.movies_api.delete_movie(movie_id)

    @allure_test_details(
        story="Фильтрация",
        title="Тест фильтрации фильмов по жанру",
        description="Этот тест проверяет, что фильтр по `genreId` работает корректно.",
        severity=allure.severity_level.NORMAL,
    )
    def test_get_movies_genre_filter(self, api_manager):
        params = {"genreId": 1}
        LOGGER.info(f"Запуск теста: test_get_movies_genre_filter с параметрами {params}")
        with allure.step(f"Отправка GET-запроса с фильтром по жанру: {params}"):
            LOGGER.info(LogMessages.Movies.ATTEMPT_GET_LIST.format(params))
            response = api_manager.movies_api.get_movies(params=params)
        is_list = isinstance(response, MoviesList)
        check.is_true(is_list, f"Ожидался объект MoviesList, но получен {type(response)}")
        if is_list:
            with allure.step("Проверка, что все полученные фильмы имеют genreId=1"):
                for movie in response.movies:
                    check.equal(movie.genre_id, 1)

    @allure_test_details(
        story="Сортировка",
        title="Тест сортировки фильмов по дате создания",
        description="Этот тест проверяет, что сортировка `createdAt: desc` работает корректно.",
        severity=allure.severity_level.NORMAL,
    )
    def test_get_movies_sort_created_at(self, api_manager):
        params = {"createdAt": "desc"}
        LOGGER.info(f"Запуск теста: test_get_movies_sort_created_at с параметрами {params}")
        with allure.step(f"Отправка GET-запроса с сортировкой по дате: {params}"):
            LOGGER.info(LogMessages.Movies.ATTEMPT_GET_LIST.format(params))
            response = api_manager.movies_api.get_movies(params=params)
        is_list = isinstance(response, MoviesList)
        check.is_true(is_list, f"Ожидался объект MoviesList, но получен {type(response)}")
        if is_list:
            with allure.step("Проверка, что фильмы отсортированы по дате создания в порядке убывания"):
                dates = [movie.created_at for movie in response.movies]
                check.equal(dates, sorted(dates, reverse=True), "Фильмы не отсортированы по убыванию даты")

    @allure_test_details(
        story="Фильтрация",
        title="Тест получения опубликованных фильмов по умолчанию",
        description="Этот тест проверяет, что по умолчанию API возвращает только опубликованные фильмы (`published: true`).",
        severity=allure.severity_level.NORMAL,
    )
    def test_get_movies_published_default(self, api_manager):
        LOGGER.info("Запуск теста: test_get_movies_published_default")
        with allure.step("Отправка GET-запроса без параметра 'published'"):
            LOGGER.info(LogMessages.Movies.ATTEMPT_GET_LIST.format("published: default"))
            response = api_manager.movies_api.get_movies()
        is_list = isinstance(response, MoviesList)
        check.is_true(is_list, f"Ожидался объект MoviesList, но получен {type(response)}")
        if is_list:
            with allure.step("Проверка, что все полученные фильмы имеют статус 'published: true'"):
                for movie in response.movies:
                    check.is_true(movie.published)

    @allure_test_details(
        story="Фильтрация",
        title="Тест фильтрации неопубликованных фильмов",
        description="Этот тест проверяет, что при запросе с флагом 'published=false' в ответе приходят только неопубликованные фильмы.",
        severity=allure.severity_level.NORMAL,
    )
    @pytest.mark.xfail(reason="API bug: returns published movies when unpublished are requested")
    def test_get_movies_unpublished(self, admin_api_manager):
        LOGGER.info("Запуск теста: test_get_movies_unpublished с параметрами {'published': False}")
        with allure.step("Запрос списка неопубликованных фильмов"):
            response = admin_api_manager.movies_api.get_movies(params={"published": False})
        is_list = isinstance(response, MoviesList)
        check.is_true(is_list, f"Ожидался объект MoviesList, но получен {type(response)}")
        if is_list:
            with allure.step("Проверка, что все полученные фильмы имеют статус 'published: false'"):
                for movie in response.movies:
                    check.is_false(movie.published)

    @allure_test_details(
        story="Невалидные параметры запроса",
        title="Тест запроса с невалидным размером страницы",
        description="Этот тест проверяет, что API возвращает ошибку 400 при некорректном значении `pageSize`.",
        severity=allure.severity_level.MINOR,
    )
    @pytest.mark.parametrize("params", [{"pageSize": "abc"}, {"pageSize": 0}, {"pageSize": 21}])
    def test_invalid_page_size(self, api_manager, params):
        allure.dynamic.title(f"Тест с невалидным pageSize: {params['pageSize']}")
        LOGGER.info(f"Запуск теста: test_invalid_page_size с параметрами {params}")
        with allure.step(f"Отправка GET-запроса с невалидным размером страницы: {params}"):
            LOGGER.info(LogMessages.Movies.ATTEMPT_GET_LIST_INVALID.format(params))
            response = api_manager.movies_api.get_movies_with_invalid_params(params=params, expected_status=400)
        with allure.step("Проверка, что ответ содержит ошибку 400 и упоминание 'pageSize'"):
            is_error = isinstance(response, ErrorResponse)
            check.is_true(is_error, f"Ожидался объект ErrorResponse, но получен {type(response)}")
            if is_error:
                check.equal(response.statusCode, 400)
                check.is_in("pageSize", str(response.message))

    @allure_test_details(
        story="Невалидные параметры запроса",
        title="Тест запроса с невалидной локацией",
        description="Этот тест проверяет, что API возвращает ошибку 400 при передаче несуществующей локации.",
        severity=allure.severity_level.MINOR,
    )
    def test_invalid_location(self, api_manager):
        params = {"locations": ["NY"]}
        LOGGER.info(f"Запуск теста: test_invalid_location с параметрами {params}")
        with allure.step(f"Отправка GET-запроса с невалидной локацией: {params}"):
            LOGGER.info(LogMessages.Movies.ATTEMPT_GET_LIST_INVALID.format(params))
            response = api_manager.movies_api.get_movies_with_invalid_params(params=params, expected_status=400)
        with allure.step("Проверка, что ответ содержит ошибку 400 и упоминание 'locations'"):
            is_error = isinstance(response, ErrorResponse)
            check.is_true(is_error, f"Ожидался объект ErrorResponse, но получен {type(response)}")
            if is_error:
                check.equal(response.statusCode, 400)
                check.equal(response.message, "Некорректные данные")

    @allure_test_details(
        story="Невалидные параметры запроса",
        title="Тест запроса с невалидным значением сортировки",
        description="Этот тест проверяет, что API возвращает ошибку 400, если в `createdAt` передано не 'asc' или 'desc'.",
        severity=allure.severity_level.MINOR,
    )
    def test_invalid_created_at_enum(self, api_manager):
        params = {"createdAt": "random"}
        LOGGER.info(f"Запуск теста: test_invalid_created_at_enum с параметрами {params}")
        with allure.step(f"Отправка GET-запроса с невалидным значением сортировки: {params}"):
            LOGGER.info(LogMessages.Movies.ATTEMPT_GET_LIST_INVALID.format(params))
            response = api_manager.movies_api.get_movies_with_invalid_params(params=params, expected_status=400)
        with allure.step("Проверка, что ответ содержит ошибку 400 и корректное сообщение"):
            is_error = isinstance(response, ErrorResponse)
            check.is_true(is_error, f"Ожидался объект ErrorResponse, но получен {type(response)}")
            if is_error:
                check.equal(response.statusCode, 400)
                check.equal(response.message, "Некорректные данные")

    @allure_test_details(
        story="Невалидные параметры запроса",
        title="Тест запроса с невалидным ID жанра",
        description="Этот тест проверяет, что API возвращает ошибку 400 при некорректном значении `genreId`.",
        severity=allure.severity_level.MINOR,
    )
    def test_invalid_genre_id(self, api_manager):
        params = {"genreId": 0}
        LOGGER.info(f"Запуск теста: test_invalid_genre_id с параметрами {params}")
        with allure.step(f"Отправка GET-запроса с невалидным ID жанра: {params}"):
            LOGGER.info(LogMessages.Movies.ATTEMPT_GET_LIST_INVALID.format(params))
            response = api_manager.movies_api.get_movies_with_invalid_params(params=params, expected_status=400)
        with allure.step("Проверка, что ответ содержит ошибку 400 и упоминание 'genreId'"):
            is_error = isinstance(response, ErrorResponse)
            check.is_true(is_error, f"Ожидался объект ErrorResponse, но получен {type(response)}")
            if is_error:
                check.equal(response.statusCode, 400)
                LOGGER.info(f"Получена ожидаемая ошибка 400. Ответ: {response.message}")
                check.is_in("genreId", str(response.message))
