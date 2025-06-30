import random
import logging
import string
from faker import Faker
from tests.models.request_models import MovieCreate, UserCreate
from tests.models.movie_models import Location, GenreId

faker = Faker("ru_RU")
logger = logging.getLogger(__name__)

class MovieDataGenerator:

    LOCATION = [Location.MSK, Location.SPB]

    @staticmethod
    def generate_random_title():
        return f"{faker.catch_phrase()} {faker.color_name()}"

    @staticmethod
    def generate_random_description(max_nb_chars=50):
        return faker.text(max_nb_chars=max_nb_chars)

    @staticmethod
    def generate_random_price(min_price=100, max_price=1000):
        return random.randint(min_price, max_price)

    @staticmethod
    def generate_random_location():
        return random.choice(MovieDataGenerator.LOCATION)

    @staticmethod
    def generate_random_genre() -> GenreId:
        return random.choice(list(GenreId))

    @staticmethod
    def generate_random_published():
        return random.choice([True, False])

    @staticmethod
    def generate_valid_movie_payload() -> MovieCreate:
        payload = MovieCreate(
            name=MovieDataGenerator.generate_random_title(),
            description=MovieDataGenerator.generate_random_description(),
            price=MovieDataGenerator.generate_random_price(),
            location=MovieDataGenerator.generate_random_location(),
            genre_id=MovieDataGenerator.generate_random_genre(),
            published=MovieDataGenerator.generate_random_published(),
        )
        logger.debug(f"Сгенерированы данные для создания фильма: {payload.model_dump_json(indent=2)}")
        return payload

class UserDataGenerator:

    @staticmethod
    def generate_user_payload() -> tuple[UserCreate, str]:
        password = UserDataGenerator.generate_random_password()
        user_data = UserCreate(
            email=UserDataGenerator.generate_random_email(),
            full_name=UserDataGenerator.generate_random_name(),
            password=password
        )
        logger.debug(f"Сгенерированы данные для создания пользователя: Email - {user_data.email}")
        return user_data, password

    @staticmethod
    def generate_random_email():
        return faker.safe_email()

    @staticmethod
    def generate_random_name():
        first_name = "".join(random.choices(string.ascii_lowercase, k=6))
        last_name = "".join(random.choices(string.ascii_lowercase, k=8))
        return f"{first_name.capitalize()} {last_name.capitalize()}"

    @staticmethod
    def generate_random_password(length=12, special_chars=False, digits=True, upper_case=True, lower_case=True):
        return faker.password(
            length=length,
            special_chars=special_chars,
            digits=digits,
            upper_case=upper_case,
            lower_case=lower_case
        )