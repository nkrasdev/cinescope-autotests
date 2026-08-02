import pytest

from tests.utils.data_generator import MovieDataGenerator, UserDataGenerator


def test_generate_random_email_avoids_reserved_example_domains() -> None:
    generated_email = UserDataGenerator.generate_random_email()
    domain = generated_email.split("@", maxsplit=1)[1]

    assert domain not in {"example.com", "example.org", "example.net"}


def test_generate_random_name_normalizes_unsupported_characters() -> None:
    class _FakeNameProvider:
        @staticmethod
        def name() -> str:
            return "Фёкла-Петрова 123"

    normalized = UserDataGenerator.generate_random_name(_FakeNameProvider())

    assert normalized == "Фекла Петрова"


def test_generate_random_price_rejects_inverted_range() -> None:
    with pytest.raises(ValueError, match="min_price"):
        MovieDataGenerator.generate_random_price(min_price=200, max_price=100)
