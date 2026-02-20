from datetime import datetime

from tests.constants.payment_data import PAYMENT_CARD
from tests.constants.ui_data import EXP_YEAR


def test_payment_card_expiration_is_not_in_past() -> None:
    exp_date = str(PAYMENT_CARD["expirationDate"])
    exp_month_str, exp_year_str = exp_date.split("/")
    exp_month = int(exp_month_str)
    exp_year = int(exp_year_str)

    now = datetime.now()
    current_two_digit_year = now.year % 100

    assert 1 <= exp_month <= 12
    assert exp_year >= current_two_digit_year


def test_ui_exp_year_is_not_in_past() -> None:
    current_year = datetime.now().year
    assert int(EXP_YEAR) >= current_year
