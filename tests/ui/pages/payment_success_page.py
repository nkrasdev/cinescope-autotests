from playwright.sync_api import Page, expect, Locator
from tests.ui.pages.base_page import BasePage

class PaymentSuccessPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.success_message_popup: Locator = page.get_by_text("Спасибо за покупку")
        self.back_to_main_button: Locator = page.get_by_role("button", name="Вернуться на главную")

    def check_success_message_is_visible(self):
        expect(self.success_message_popup).to_be_visible()

    def click_back_to_main_button(self):
        self.back_to_main_button.click() 