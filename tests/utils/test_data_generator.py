from faker import Faker

from tests.utils.data_generator import UserDataGenerator


def test_generate_random_email_avoids_reserved_example_domains() -> None:
    faker = Faker("ru_RU")

    generated_email = UserDataGenerator.generate_random_email(faker)
    domain = generated_email.split("@", maxsplit=1)[1]

    assert domain not in {"example.com", "example.org", "example.net"}


def test_generate_random_name_normalizes_unsupported_characters() -> None:
    class _FakeNameProvider:
        @staticmethod
        def name() -> str:
            return "Фёкла-Петрова 123"

    normalized = UserDataGenerator.generate_random_name(_FakeNameProvider())  # type: ignore[arg-type]

    assert normalized == "Фекла Петрова"
