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
    return {
        "email": faker_instance.email(),
        "fullName": faker_instance.name(),
        "password": UserDataGenerator.generate_random_password()
    }

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
        create_response = admin_api_manager.movies_api.create_movie(
            movie_data=movie_payload,
            expected_status=201
        )
        created_movie_data = create_response.json()
        movie_id = created_movie_data["id"]

        yield created_movie_data

    finally:
        if movie_id:
            admin_api_manager.movies_api.delete_movie(movie_id, expected_status=200)
