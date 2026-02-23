import logging
import os
from collections.abc import Generator
from pathlib import Path

import allure
import pytest
import requests
from faker import Faker

from tests.clients.api_manager import ApiManager
from tests.constants.endpoints import BASE_URL
from tests.models.movie_models import Movie
from tests.models.request_models import MovieCreate, UserCreate
from tests.models.user_models import User
from tests.utils.data_generator import MovieDataGenerator, UserDataGenerator
from tests.utils.logging_utils import LegacyMessageFilter, log_event

LOGGER = logging.getLogger(__name__)
_LEGACY_FILTER_STATE = {"installed": False}


def _install_legacy_message_filter() -> None:
    if _LEGACY_FILTER_STATE["installed"]:
        return
    logging.getLogger().addFilter(LegacyMessageFilter())
    _LEGACY_FILTER_STATE["installed"] = True


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
def allure_layer_labels(request):
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


def pytest_sessionstart(session):
    _install_legacy_message_filter()

    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    screenshots_dir = os.path.join(logs_dir, "screenshots")
    if not os.path.exists(screenshots_dir):
        os.makedirs(screenshots_dir)

    log_event(LOGGER, "session", "start")


def pytest_runtest_setup(item):
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


@pytest.fixture(scope="session")
def faker_instance() -> Faker:
    return Faker("ru_RU")


@pytest.fixture(scope="function")
def api_manager() -> Generator[ApiManager]:
    session = requests.Session()
    manager = ApiManager(session, base_url=BASE_URL)
    try:
        yield manager
    finally:
        session.close()


@pytest.fixture()
def user_credentials(faker_instance) -> tuple[UserCreate, str]:
    return UserDataGenerator.generate_user_payload(faker_instance)


@pytest.fixture()
def movie_payload(faker_instance) -> MovieCreate:
    return MovieDataGenerator.generate_valid_movie_payload(faker_instance)


@pytest.fixture()
def user_credentials_ui(faker_instance) -> tuple[UserCreate, str]:
    return UserDataGenerator.generate_user_payload(faker_instance)


@pytest.fixture(scope="function")
def admin_api_manager() -> Generator[ApiManager]:
    session = requests.Session()
    manager = ApiManager(session, base_url=BASE_URL)
    manager.auth_api.login()
    try:
        yield manager
    finally:
        session.close()


@pytest.fixture
def created_movie(admin_api_manager, movie_payload: MovieCreate):
    log_event(LOGGER, "fixture", "start", fixture="created_movie")
    movie_id = None
    try:
        created_movie_model = admin_api_manager.movies_api.create_movie(movie_data=movie_payload, expected_status=201)
        assert isinstance(created_movie_model, Movie), "Фикстура 'created_movie' ожидала успешного создания фильма"
        movie_id = created_movie_model.id
        log_event(
            LOGGER, "fixture", "resource_created", fixture="created_movie", resource="movie", resource_id=movie_id
        )

        yield created_movie_model

    finally:
        if movie_id:
            log_event(
                LOGGER,
                "fixture",
                "cleanup_start",
                fixture="created_movie",
                resource="movie",
                resource_id=movie_id,
            )
            try:
                admin_api_manager.movies_api.delete_movie(movie_id, expected_status=200)
                log_event(
                    LOGGER,
                    "fixture",
                    "cleanup_success",
                    fixture="created_movie",
                    resource="movie",
                    resource_id=movie_id,
                )
            except AssertionError:
                log_event(
                    LOGGER,
                    "fixture",
                    "cleanup_skip",
                    level=logging.WARNING,
                    fixture="created_movie",
                    resource="movie",
                    resource_id=movie_id,
                    reason="already_deleted_or_unavailable",
                )


@pytest.fixture
def created_movie_unpublished(admin_api_manager, movie_payload: MovieCreate):
    log_event(LOGGER, "fixture", "start", fixture="created_movie_unpublished")
    movie_id = None
    payload = movie_payload.model_copy(update={"published": False})
    try:
        created_movie_model = admin_api_manager.movies_api.create_movie(movie_data=payload, expected_status=201)
        assert isinstance(created_movie_model, Movie), (
            "Фикстура 'created_movie_unpublished' ожидала успешного создания фильма"
        )
        movie_id = created_movie_model.id
        log_event(
            LOGGER,
            "fixture",
            "resource_created",
            fixture="created_movie_unpublished",
            resource="movie",
            resource_id=movie_id,
        )

        yield created_movie_model

    finally:
        if movie_id:
            log_event(
                LOGGER,
                "fixture",
                "cleanup_start",
                fixture="created_movie_unpublished",
                resource="movie",
                resource_id=movie_id,
            )
            try:
                admin_api_manager.movies_api.delete_movie(movie_id, expected_status=200)
                log_event(
                    LOGGER,
                    "fixture",
                    "cleanup_success",
                    fixture="created_movie_unpublished",
                    resource="movie",
                    resource_id=movie_id,
                )
            except AssertionError:
                log_event(
                    LOGGER,
                    "fixture",
                    "cleanup_skip",
                    level=logging.WARNING,
                    fixture="created_movie_unpublished",
                    resource="movie",
                    resource_id=movie_id,
                    reason="already_deleted_or_unavailable",
                )


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed and "page" in item.funcargs:
        page = item.funcargs["page"]
        screenshots_dir = os.path.join("logs", "screenshots")
        screenshot_path = os.path.join(screenshots_dir, f"{item.name}_failure.png")
        page.screenshot(path=screenshot_path)
        log_event(
            LOGGER,
            "artifact",
            "saved",
            nodeid=item.nodeid,
            artifact_type="screenshot",
            path=screenshot_path,
        )
        allure.attach.file(
            screenshot_path,
            name="screenshot",
            attachment_type=allure.attachment_type.PNG,
        )


@pytest.fixture
def registered_user_by_api_ui(
    api_manager: ApiManager, admin_api_manager: ApiManager, user_credentials_ui: tuple[UserCreate, str]
) -> Generator[UserCreate]:
    user_payload, password_repeat = user_credentials_ui
    register_data = user_payload.model_dump(by_alias=True)
    register_data["passwordRepeat"] = password_repeat
    response = api_manager.auth_api.register(user_data=register_data, expected_status=201)
    user_id = response.id if isinstance(response, User) else None
    try:
        yield user_payload
    finally:
        if user_id:
            try:
                admin_api_manager.users_api.delete_user(user_id, expected_status=200)
            except AssertionError:
                log_event(
                    LOGGER,
                    "fixture",
                    "cleanup_skip",
                    level=logging.WARNING,
                    fixture="registered_user_by_api_ui",
                    resource="user",
                    resource_id=user_id,
                    reason="already_deleted_or_unavailable",
                )


@pytest.fixture
def new_registered_user(
    user_credentials: tuple[UserCreate, str],
) -> Generator[tuple[ApiManager, UserCreate]]:
    log_event(LOGGER, "fixture", "start", fixture="new_registered_user")
    user_payload, password_repeat = user_credentials
    session = requests.Session()
    api_manager = ApiManager(session, base_url=BASE_URL)

    user_id = None
    try:
        register_data = user_payload.model_dump(by_alias=True)
        register_data["passwordRepeat"] = password_repeat
        registration_response = api_manager.auth_api.register(user_data=register_data, expected_status=201)
        assert isinstance(registration_response, User), "Фикстура 'new_registered_user' ожидала успешной регистрации"
        log_event(
            LOGGER,
            "fixture",
            "resource_created",
            fixture="new_registered_user",
            resource="user",
            email=user_payload.email,
            resource_id=registration_response.id,
        )
        user_id = registration_response.id

    except ValueError as e:
        log_event(
            LOGGER,
            "fixture",
            "error",
            level=logging.ERROR,
            fixture="new_registered_user",
            email=user_payload.email,
            error=str(e),
        )
        pytest.fail(f"Регистрация прервана с непредвиденной ошибкой: {e}")

    if "Authorization" in api_manager.session.headers:
        del api_manager.session.headers["Authorization"]

    yield api_manager, user_payload
    if user_id:
        try:
            api_manager.auth_api.login(email=user_payload.email, password=user_payload.password, expected_status=200)
            api_manager.users_api.delete_user(user_id, expected_status=200)
        except AssertionError:
            log_event(
                LOGGER,
                "fixture",
                "cleanup_skip",
                level=logging.WARNING,
                fixture="new_registered_user",
                resource="user",
                resource_id=user_id,
                reason="already_deleted_or_unavailable",
            )
    session.close()
    log_event(LOGGER, "fixture", "finish", fixture="new_registered_user", email=user_payload.email)
