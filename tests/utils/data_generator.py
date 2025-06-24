import random
from faker import Faker

faker = Faker("ru_RU")

class MovieDataGenerator:

    GENRE = [1, 2, 3, 4, 5]
    LOCATION = ["MSK", "SPB"]

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
    def generate_random_genre():
        return random.choice(MovieDataGenerator.GENRE)

    @staticmethod
    def generate_random_published():
        return True

    @staticmethod
    def generate_valid_movie_payload():
        return {
            "name": MovieDataGenerator.generate_random_title(),
            "description": MovieDataGenerator.generate_random_description(),
            "price": MovieDataGenerator.generate_random_price(),
            "location": MovieDataGenerator.generate_random_location(),
            "genreId": MovieDataGenerator.generate_random_genre(),
            "published": MovieDataGenerator.generate_random_published(),
        }

class UserDataGenerator:

    @staticmethod
    def generate_random_email():
        return faker.email()

    @staticmethod
    def generate_random_name():
        return faker.name()

    @staticmethod
    def generate_random_password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True):
        return faker.password(
            length=length,
            special_chars=special_chars,
            digits=digits,
            upper_case=upper_case,
            lower_case=lower_case
        )