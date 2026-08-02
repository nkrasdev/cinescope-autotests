from unittest.mock import Mock, patch

from tests.clients.payment_api import PaymentAPI
from tests.models.payment_models import PaymentResult, PaymentStatus


def test_create_payment_extracts_status_from_nested_error() -> None:
    session = Mock()
    session.headers = {}
    payment_api = PaymentAPI(session=session, base_url="https://payment.example.test")
    response = Mock(ok=False)
    response.json.return_value = {
        "message": "Неверная карта",
        "error": {"status": "INVALID_CARD"},
    }

    with patch.object(payment_api, "post", return_value=response):
        result = payment_api.create_payment({"movieId": 1}, expected_status=None)

    assert isinstance(result, PaymentResult)
    assert result.status is PaymentStatus.INVALID_CARD
