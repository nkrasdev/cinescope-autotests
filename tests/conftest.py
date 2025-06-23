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
    """
    Менеджер с валидным админ-токеном сразу в headers.
    Подходит для всех позитивных сценариев (201/200 и т.д.).
    """
    session = requests.Session()
    manager = ApiManager(session, base_url=BASE_URL)

    manager.auth_api.login()

    return manager
