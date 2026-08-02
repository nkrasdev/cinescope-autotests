import logging
import re
import secrets
from typing import Any, Protocol
from uuid import uuid4

from faker import Faker

from tests.models.movie_models import Location
from tests.models.request_models import MovieCreate, UserCreate
from tests.utils.logging_utils import log_event

LOGGER = logging.getLogger(__name__)
_UNSUPPORTED_NAME_CHARACTERS = re.compile(r"[^А-Яа-я ]")
_REPEATED_WHITESPACE = re.compile(r"\s+")


class NameProvider(Protocol):
    def name(self) -> str: ...


class MovieDataGenerator:
    LOCATIONS = (Location.MSK, Location.SPB)
    DEFAULT_GENRE_ID = 1

    @staticmethod
    def generate_random_title(faker: Faker) -> str:
        return f"{faker.catch_phrase()} {faker.color_name()}"

    @staticmethod
    def generate_random_description(faker: Faker, max_nb_chars: int = 50) -> str:
        return faker.text(max_nb_chars=max_nb_chars)

    @staticmethod
    def generate_random_price(min_price: int = 100, max_price: int = 1000) -> int:
        if min_price > max_price:
            raise ValueError("min_price не может быть больше max_price")
        return min_price + secrets.randbelow(max_price - min_price + 1)

    @staticmethod
    def generate_random_location() -> Location:
        return secrets.choice(MovieDataGenerator.LOCATIONS)

    @staticmethod
    def generate_random_published() -> bool:
        return secrets.choice([True, False])

    @staticmethod
    def generate_valid_movie_payload(
        faker: Faker,
        *,
        genre_id: int = DEFAULT_GENRE_ID,
    ) -> MovieCreate:
        movie_payload = MovieCreate.model_validate(
            {
                "name": MovieDataGenerator.generate_random_title(faker),
                "description": MovieDataGenerator.generate_random_description(faker),
                "price": MovieDataGenerator.generate_random_price(),
                "location": MovieDataGenerator.generate_random_location(),
                "genre_id": genre_id,
                "published": MovieDataGenerator.generate_random_published(),
            }
        )
        log_event(
            LOGGER,
            "generator",
            "movie_payload_created",
            level=logging.DEBUG,
            name=movie_payload.name,
            location=movie_payload.location.value,
            genre_id=movie_payload.genre_id,
        )
        return movie_payload

    @staticmethod
    def generate_movie_payload_missing_field(faker: Faker, field: str) -> dict[str, Any]:
        movie_payload = MovieDataGenerator.generate_valid_movie_payload(faker).model_dump(by_alias=True)
        movie_payload.pop(field, None)
        return movie_payload

    @staticmethod
    def generate_movie_payload_with_invalid_field(
        faker: Faker, field: str, value: Any, *, by_alias: bool = True
    ) -> dict[str, Any]:
        movie_payload = MovieDataGenerator.generate_valid_movie_payload(faker).model_dump(by_alias=by_alias)
        movie_payload[field] = value
        return movie_payload


class UserDataGenerator:
    @staticmethod
    def generate_user_payload(faker: Faker) -> tuple[UserCreate, str]:
        password = UserDataGenerator.generate_random_password(faker)
        user_data = UserCreate(
            email=UserDataGenerator.generate_random_email(),
            full_name=UserDataGenerator.generate_random_name(faker),
            password=password,
        )
        log_event(LOGGER, "generator", "user_payload_created", level=logging.DEBUG, email=user_data.email)
        return user_data, password

    @staticmethod
    def generate_random_email() -> str:
        return f"autotest-{uuid4().hex[:12]}@gmail.com"

    @staticmethod
    def generate_random_name(faker: NameProvider) -> str:
        raw_name = faker.name().translate(str.maketrans({"Ё": "Е", "ё": "е"}))
        normalized_name = _UNSUPPORTED_NAME_CHARACTERS.sub(" ", raw_name)
        normalized_name = _REPEATED_WHITESPACE.sub(" ", normalized_name).strip()
        return normalized_name

    @staticmethod
    def generate_random_password(
        faker: Faker,
        length: int = 12,
        special_chars: bool = False,
        digits: bool = True,
        upper_case: bool = True,
        lower_case: bool = True,
    ) -> str:
        return faker.password(
            length=length,
            special_chars=special_chars,
            digits=digits,
            upper_case=upper_case,
            lower_case=lower_case,
        )
