from tests.models.response_models import ErrorResponse


def test_error_response_message_text_returns_single_message() -> None:
    error = ErrorResponse.model_validate({"statusCode": 400, "message": "Некорректные данные"})

    assert error.message_text == "Некорректные данные"


def test_error_response_message_text_joins_validation_messages() -> None:
    error = ErrorResponse.model_validate({"statusCode": 400, "message": ["name is required", "price must be positive"]})

    assert error.message_text == "name is required price must be positive"
