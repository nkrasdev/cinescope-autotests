import pytest
import requests
import logging
import os
from logging.handlers import RotatingFileHandler
from faker import Faker
from clients.api_manager import ApiManager
from tests.constants.endpoints import BASE_URL
from tests.constants.log_messages import LogMessages
from utils.data_generator import MovieDataGenerator, UserDataGenerator
from tests.models.request_models import UserCreate, MovieCreate
from tests.models.user_models import User
from tests.models.movie_models import Movie
from typing import Generator

LOGGER = logging.getLogger(__name__)

def pytest_sessionstart(session):
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    log_file = os.path.join(logs_dir, "tests.log")

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    root_logger.addHandler(file_handler)

    LOGGER.info(LogMessages.General.SESSION_START)

@pytest.fixture(scope="session")
def faker_instance() -> Faker:
    return Faker("ru_RU")

@pytest.fixture(scope="function")
def api_manager() -> ApiManager:
    return ApiManager(requests.Session(), base_url=BASE_URL)

@pytest.fixture()
def user_credentials(faker_instance) -> tuple[UserCreate, str]:
    return UserDataGenerator.generate_user_payload()

@pytest.fixture()
def movie_payload() -> MovieCreate:
    return MovieDataGenerator.generate_valid_movie_payload()

@pytest.fixture()
def user_credentials_ui(faker_instance) -> tuple[UserCreate, str]:
    return UserDataGenerator.generate_user_payload()

@pytest.fixture(scope="function")
def admin_api_manager(api_manager: ApiManager) -> ApiManager:
    api_manager.auth_api.login()
    return api_manager

@pytest.fixture
def created_movie(admin_api_manager, movie_payload: MovieCreate):
    LOGGER.info("Фикстура 'created_movie': создаем фильм.")
    movie_id = None
    try:
        created_movie_model = admin_api_manager.movies_api.create_movie(
            movie_data=movie_payload,
            expected_status=201
        )
        assert isinstance(created_movie_model, Movie), "Фикстура 'created_movie' ожидала успешного создания фильма"
        movie_id = created_movie_model.id
        LOGGER.info(f"Фильм с ID {movie_id} успешно создан фикстурой.")

        yield created_movie_model

    finally:
        if movie_id:
            LOGGER.info(f"Фикстура 'created_movie': удаляем фильм с ID {movie_id}.")
            try:
                admin_api_manager.movies_api.delete_movie(movie_id, expected_status=200)
                LOGGER.info(f"Фильм с ID {movie_id} успешно удален фикстурой.")
            except AssertionError:
                LOGGER.warning(f"Не удалось удалить фильм с ID {movie_id} в teardown фикстуры. Возможно, он уже был удален в тесте.")

@pytest.fixture
def registered_user_by_api_ui(api_manager: ApiManager, user_credentials_ui: tuple[UserCreate, str]) -> UserCreate:
    user_payload, password_repeat = user_credentials_ui
    register_data = user_payload.model_dump(by_alias=True)
    register_data["passwordRepeat"] = password_repeat
    api_manager.auth_api.register(user_data=register_data, expected_status=201)
    return user_payload

@pytest.fixture
def new_registered_user(user_credentials: tuple[UserCreate, str]) -> Generator[tuple[ApiManager, UserCreate], None, None]:
    LOGGER.info("Фикстура 'new_registered_user': регистрируем нового пользователя.")
    user_payload, password_repeat = user_credentials
    session = requests.Session()
    api_manager = ApiManager(session, base_url=BASE_URL)

    try:
        register_data = user_payload.model_dump(by_alias=True)
        register_data["passwordRepeat"] = password_repeat
        registration_response = api_manager.auth_api.register(user_data=register_data, expected_status=201)
        assert isinstance(registration_response, User), "Фикстура 'new_registered_user' ожидала успешной регистрации"
        LOGGER.info(f"Пользователь с email {user_payload.email} успешно зарегистрирован фикстурой.")

    except ValueError as e:
        LOGGER.error(f"Регистрация пользователя {user_payload.email} провалилась: {e}")
        pytest.fail(f"Регистрация прервана с непредвиденной ошибкой: {e}")

    if "Authorization" in api_manager.session.headers:
        del api_manager.session.headers["Authorization"]

    yield api_manager, user_payload
    LOGGER.info(f"Фикстура 'new_registered_user' для пользователя {user_payload.email} завершила свою работу.")
