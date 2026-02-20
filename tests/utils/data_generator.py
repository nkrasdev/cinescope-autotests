import logging
import re
import secrets
from typing import Any
from uuid import uuid4

from faker import Faker

from tests.models.movie_models import GenreId, Location
from tests.models.request_models import MovieCreate, UserCreate

logger = logging.getLogger(__name__)


class MovieDataGenerator:
    LOCATION = [Location.MSK, Location.SPB]

    @staticmethod
    def generate_random_title(faker: Faker):
        return f"{faker.catch_phrase()} {faker.color_name()}"

    @staticmethod
    def generate_random_description(faker: Faker, max_nb_chars=50):
        return faker.text(max_nb_chars=max_nb_chars)

    @staticmethod
    def generate_random_price(min_price=100, max_price=1000):
        return min_price + secrets.randbelow(max_price - min_price + 1)

    @staticmethod
    def generate_random_location():
        return secrets.choice(MovieDataGenerator.LOCATION)

    @staticmethod
    def generate_random_genre() -> GenreId:
        return secrets.choice(list(GenreId))

    @staticmethod
    def generate_random_published():
        return secrets.choice([True, False])

    @staticmethod
    def generate_valid_movie_payload(faker: Faker) -> MovieCreate:
        payload = MovieCreate(
            name=MovieDataGenerator.generate_random_title(faker),
            description=MovieDataGenerator.generate_random_description(faker),
            price=MovieDataGenerator.generate_random_price(),
            location=MovieDataGenerator.generate_random_location(),
            genreId=MovieDataGenerator.generate_random_genre(),
            published=MovieDataGenerator.generate_random_published(),
        )
        logger.debug(f"Сгенерированы данные для создания фильма: {payload.model_dump_json(indent=2)}")
        return payload

    @staticmethod
    def generate_movie_payload_missing_field(faker: Faker, field: str) -> dict[str, Any]:
        payload = MovieDataGenerator.generate_valid_movie_payload(faker).model_dump(by_alias=True)
        payload.pop(field, None)
        return payload

    @staticmethod
    def generate_movie_payload_with_invalid_field(
        faker: Faker, field: str, value: Any, *, by_alias: bool = True
    ) -> dict[str, Any]:
        payload = MovieDataGenerator.generate_valid_movie_payload(faker).model_dump(by_alias=by_alias)
        payload[field] = value
        return payload


class UserDataGenerator:
    @staticmethod
    def generate_user_payload(faker: Faker) -> tuple[UserCreate, str]:
        password = UserDataGenerator.generate_random_password(faker)
        user_data = UserCreate(
            email=UserDataGenerator.generate_random_email(faker),
            full_name=UserDataGenerator.generate_random_name(faker),
            password=password,
        )
        logger.debug(f"Сгенерированы данные для создания пользователя: Email - {user_data.email}")
        return user_data, password

    @staticmethod
    def generate_random_email(faker: Faker):
        return f"autotest-{uuid4().hex[:12]}@gmail.com"

    @staticmethod
    def generate_random_name(faker: Faker):
        raw_name = faker.name().replace("Ё", "Е").replace("ё", "е")
        normalized_name = re.sub(r"[^А-Яа-я ]", " ", raw_name)
        normalized_name = re.sub(r"\s+", " ", normalized_name).strip()
        return normalized_name

    @staticmethod
    def generate_random_password(
        faker: Faker,
        length=12,
        special_chars=False,
        digits=True,
        upper_case=True,
        lower_case=True,
    ):
        return faker.password(
            length=length,
            special_chars=special_chars,
            digits=digits,
            upper_case=upper_case,
            lower_case=lower_case,
        )
