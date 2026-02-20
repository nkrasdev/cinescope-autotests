from playwright.sync_api import Locator, Page, expect

from tests.constants.timeouts import Timeout
from tests.ui.pages.base_page import BasePage


class PaymentPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.movie_title: Locator = page.locator("h3", has_text="Покупка билета").locator("xpath=following-sibling::p")
        self.price: Locator = page.locator("div:has(label:text('Сумма к оплате')) p.text-3xl")
        self.amount_input: Locator = page.locator("#amount")
        self.card_number_input: Locator = page.locator("#card\\.cardNumber")
        self.card_holder_input: Locator = page.locator("#card\\.cardholderName")
        self.month_select: Locator = page.get_by_role("combobox", name="Месяц")
        self.year_select: Locator = page.get_by_role("combobox", name="Год")
        self.cvc_input: Locator = page.locator("#cvc")
        self.submit_button: Locator = page.get_by_role("button", name="Оплатить")

    def open(self, movie_id: int):
        super().open(f"/payment?movieId={movie_id}")

    def fill_payment_details(
        self, card_number: str, card_holder: str, month: str, year: str, cvc: str, amount: int = 1
    ):
        self.amount_input.fill(str(amount))
        self.card_number_input.fill(card_number)
        self.card_holder_input.fill(card_holder)

        self.month_select.click()
        self.page.get_by_role("option", name=month).click()

        self.year_select.click()
        self.page.get_by_role("option", name=year).click()

        self.cvc_input.fill(cvc)

    def submit_payment(self):
        self.submit_button.click()

    def check_movie_title_is_visible(self, title_part: str):
        expect(self.movie_title).to_contain_text(title_part)

    def check_price_is_visible(self):
        expect(self.price).to_be_visible()

    def check_submit_button_is_disabled(self):
        expect(self.submit_button).to_be_disabled()

    def check_validation_error_is_visible(self, message: str):
        error_locator = self.page.get_by_text(message)
        expect(error_locator).to_be_visible(timeout=Timeout.FIVE_SECONDS.value)
