import logging
from pathlib import Path

import allure
import pytest
import requests
from faker import Faker

from tests.clients.api_manager import ApiManager
from tests.constants.endpoints import BASE_URL
from tests.models.movie_models import Movie
from tests.models.request_models import MovieCreate, UserCreate
from tests.utils.catalog_factory import GenreFactory, MovieFactory
from tests.utils.data_generator import MovieDataGenerator, UserDataGenerator
from tests.utils.logging_utils import LegacyMessageFilter, log_event
from tests.utils.user_factory import AdminUserFactory, RegisteredUserFactory
from tests.utils.xdist_groups import xdist_group_for_module

LOGGER = logging.getLogger(__name__)


def _install_legacy_message_filter() -> None:
    root_logger = logging.getLogger()
    if any(isinstance(log_filter, LegacyMessageFilter) for log_filter in root_logger.filters):
        return
    root_logger.addFilter(LegacyMessageFilter())


def _infer_allure_sub_suite(path: Path) -> str:
    stem = path.stem.lower()
    if "auth" in stem:
        return "Аутентификация"
    if "payment" in stem:
        return "Платежи"
    if "movie" in stem or "movies" in stem:
        return "Фильмы"
    if "main_page" in stem:
        return "Главная"
    return stem.replace("test_", "").replace("_", " ").title()


@pytest.fixture(autouse=True)
def allure_layer_labels(request: pytest.FixtureRequest) -> None:
    path = Path(str(request.node.fspath))
    posix_path = path.as_posix()
    if "tests/api/" in posix_path:
        suite = "API"
    elif "tests/ui/" in posix_path:
        suite = "UI"
    else:
        suite = "Other"
    allure.dynamic.parent_suite("Cinescope")
    allure.dynamic.suite(suite)
    allure.dynamic.sub_suite(_infer_allure_sub_suite(path))


def pytest_sessionstart(session: pytest.Session) -> None:
    _install_legacy_message_filter()

    Path("logs/screenshots").mkdir(parents=True, exist_ok=True)

    log_event(LOGGER, "session", "start")


def pytest_runtest_setup(item: pytest.Item) -> None:
    log_event(LOGGER, "test", "start", nodeid=item.nodeid)


def pytest_runtest_logreport(report):
    if report.when != "call":
        return

    log_event(
        LOGGER,
        "test",
        "finish",
        nodeid=report.nodeid,
        outcome=report.outcome,
        duration_sec=round(report.duration, 3),
    )


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    for item in items:
        stem = Path(item.fspath).stem
        if group := xdist_group_for_module(stem):
            item.add_marker(pytest.mark.xdist_group(group))


@pytest.fixture(scope="session")
def faker_instance() -> Faker:
    return Faker("ru_RU")


@pytest.fixture(scope="function")
def api_manager(request: pytest.FixtureRequest) -> ApiManager:
    session = requests.Session()
    request.addfinalizer(session.close)
    return ApiManager(session, base_url=BASE_URL)


@pytest.fixture()
def user_credentials(faker_instance) -> tuple[UserCreate, str]:
    return UserDataGenerator.generate_user_payload(faker_instance)


@pytest.fixture()
def movie_payload(api_manager: ApiManager, faker_instance: Faker) -> MovieCreate:
    genres = api_manager.movies_api.get_genres()
    if not isinstance(genres, list) or not genres:
        raise AssertionError("Для создания фильма требуется хотя бы один доступный жанр")
    return MovieDataGenerator.generate_valid_movie_payload(faker_instance, genre_id=genres[0].id)


@pytest.fixture(scope="session")
def admin_api_manager(request: pytest.FixtureRequest) -> ApiManager:
    """Return one authenticated admin client per pytest worker process."""
    session = requests.Session()
    request.addfinalizer(session.close)
    manager = ApiManager(session, base_url=BASE_URL)
    manager.auth_api.login()
    return manager


@pytest.fixture
def admin_user_factory(
    admin_api_manager: ApiManager,
    faker_instance: Faker,
    request: pytest.FixtureRequest,
) -> AdminUserFactory:
    factory = AdminUserFactory(admin_api_manager, faker_instance)
    request.addfinalizer(factory.cleanup)
    return factory


@pytest.fixture
def registered_user_factory(
    api_manager: ApiManager,
    admin_api_manager: ApiManager,
    faker_instance: Faker,
    request: pytest.FixtureRequest,
) -> RegisteredUserFactory:
    factory = RegisteredUserFactory(api_manager, admin_api_manager, faker_instance)
    request.addfinalizer(factory.cleanup)
    return factory


@pytest.fixture
def movie_factory(
    admin_api_manager: ApiManager,
    request: pytest.FixtureRequest,
) -> MovieFactory:
    factory = MovieFactory(admin_api_manager)
    request.addfinalizer(factory.cleanup)
    return factory


@pytest.fixture
def genre_factory(
    admin_api_manager: ApiManager,
    request: pytest.FixtureRequest,
) -> GenreFactory:
    factory = GenreFactory(admin_api_manager)
    request.addfinalizer(factory.cleanup)
    return factory


@pytest.fixture
def created_movie(movie_factory: MovieFactory, movie_payload: MovieCreate) -> Movie:
    return movie_factory.create(movie_payload.model_copy(update={"published": True}))


@pytest.fixture
def created_movie_unpublished(movie_factory: MovieFactory, movie_payload: MovieCreate) -> Movie:
    return movie_factory.create(movie_payload.model_copy(update={"published": False}))


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed and "page" in item.funcargs:
        page = item.funcargs["page"]
        screenshot_path = Path("logs/screenshots") / f"{item.name}_failure.png"
        page.screenshot(path=str(screenshot_path))
        log_event(
            LOGGER,
            "artifact",
            "saved",
            nodeid=item.nodeid,
            artifact_type="screenshot",
            path=str(screenshot_path),
        )
        allure.attach.file(
            str(screenshot_path),
            name="screenshot",
            attachment_type=allure.attachment_type.PNG,
        )


@pytest.fixture
def registered_user_by_api_ui(
    registered_user_factory: RegisteredUserFactory,
) -> UserCreate:
    return registered_user_factory.create().credentials


@pytest.fixture
def new_registered_user(
    api_manager: ApiManager,
    registered_user_factory: RegisteredUserFactory,
) -> tuple[ApiManager, UserCreate]:
    registered_user = registered_user_factory.create()
    return api_manager, registered_user.credentials
