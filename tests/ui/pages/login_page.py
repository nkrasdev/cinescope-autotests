from playwright.sync_api import Locator, Page, expect

from tests.constants.timeouts import Timeout
from tests.models.request_models import UserCreate
from tests.ui.pages.base_page import BasePage


class LoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.email_input: Locator = page.locator("#email")
        self.password_input: Locator = page.locator("#password")
        self.submit_button: Locator = page.locator("form").get_by_role("button", name="Войти")
        self.profile_button: Locator = page.get_by_role("button", name="Профиль")

    def open(self):
        super().open("/login")

    def login(self, user: UserCreate, password: str):
        self.email_input.fill(user.email)
        self.password_input.fill(password)
        self.submit_button.click()

    def check_user_is_logged_in(self):
        expect(self.page.get_by_text("Вы вошли в аккаунт")).to_be_visible(timeout=Timeout.TEN_SECONDS.value)
        expect(self.profile_button).to_be_visible()

    def check_error_message(self, message: str):
        error_locator = self.page.get_by_text(message)
        expect(error_locator).to_be_visible()
