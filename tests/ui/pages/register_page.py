from playwright.sync_api import Locator, Page, expect

from tests.constants.timeouts import Timeout
from tests.models.request_models import UserCreate
from tests.ui.pages.base_page import BasePage


class RegisterPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.full_name_input: Locator = page.locator('input[name="fullName"]')
        self.email_input: Locator = page.locator('input[name="email"]')
        self.password_input: Locator = page.locator('input[name="password"]')
        self.password_repeat_input: Locator = page.locator('input[name="passwordRepeat"]')
        self.submit_button: Locator = page.locator("form").get_by_role("button", name="Зарегистрироваться")

    def open(self):
        super().open("/register")

    def register_user(self, user: UserCreate, password_repeat: str):
        self.full_name_input.fill(user.full_name)
        self.email_input.fill(user.email)
        self.password_input.fill(user.password)
        self.password_repeat_input.fill(password_repeat)
        self.submit_button.click()

    def check_registration_is_successful(self):
        self.page.wait_for_url("**/login", timeout=Timeout.DEFAULT_TIMEOUT.value)

        success_message = self.page.get_by_text("Подтвердите свою почту")
        expect(success_message).to_be_visible(timeout=Timeout.DEFAULT_TIMEOUT.value)

    def check_error_message(self, message: str):
        error_locator = self.page.get_by_text(message)
        expect(error_locator.first).to_be_visible()
