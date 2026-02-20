from datetime import datetime

_FUTURE_2DIGIT_YEAR = f"{(datetime.now().year + 1) % 100:02d}"

PAYMENT_CARD = {
    "cardNumber": "4242424242424242",
    "cardHolder": "Test User",
    "expirationDate": f"12/{_FUTURE_2DIGIT_YEAR}",
    "securityCode": 123,
}
PAYMENT_TICKETS_AMOUNT = 1
