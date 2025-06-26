import pytest
import requests
from faker import Faker
from clients.api_manager import ApiManager
from tests.constants import BASE_URL
from utils.data_generator import MovieDataGenerator, UserDataGenerator

@pytest.fixture(scope="session")
def faker_instance() -> Faker:
    return Faker("ru_RU")

@pytest.fixture(scope="function")
def api_manager() -> ApiManager:
    return ApiManager(requests.Session(), base_url=BASE_URL)

@pytest.fixture()
def user_credentials(faker_instance):
    return UserDataGenerator.generate_user_payload()

@pytest.fixture()
def movie_payload():
    return MovieDataGenerator.generate_valid_movie_payload()

@pytest.fixture(scope="function")
def admin_api_manager() -> ApiManager:
    session = requests.Session()
    manager = ApiManager(session, base_url=BASE_URL)
    manager.auth_api.login()
    return manager

@pytest.fixture
def created_movie(admin_api_manager, movie_payload):
    movie_id = None
    try:
        created_movie_model = admin_api_manager.movies_api.create_movie(
            movie_data=movie_payload,
            expected_status=201
        )
        movie_id = created_movie_model.id

        yield created_movie_model

    finally:
        if movie_id:
            admin_api_manager.movies_api.delete_movie(movie_id, expected_status=200)

@pytest.fixture
def new_registered_user(user_credentials):
    session = requests.Session()
    api_manager = ApiManager(session, base_url=BASE_URL)

    try:
        api_manager.auth_api.register(user_data=user_credentials, expected_status=201)
    except ValueError as e:
        pytest.fail(f"Регистрация прервана с непредвиденной ошибкой: {e}")

    if "Authorization" in api_manager.session.headers:
        del api_manager.session.headers["Authorization"]

    yield api_manager, user_credentials
