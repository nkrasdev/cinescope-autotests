from playwright.sync_api import Page, expect, Locator
from tests.ui.pages.base_page import BasePage
from tests.models.request_models import UserCreate


class RegisterPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.full_name_input: Locator = page.locator('[data-qa-id="register_full_name_input"]')
        self.email_input: Locator = page.locator('[data-qa-id="register_email_input"]')
        self.password_input: Locator = page.locator('[data-qa-id="register_password_input"]')
        self.password_repeat_input: Locator = page.locator('[data-qa-id="register_password_repeat_input"]')
        self.submit_button: Locator = page.locator('[data-qa-id="register_submit_button"]')

    def open(self):
        super().open("/register")

    def register_user(self, user: UserCreate, password_repeat: str):
        self.full_name_input.fill(user.full_name)
        self.email_input.fill(user.email)
        self.password_input.fill(user.password)
        self.password_repeat_input.fill(password_repeat)
        self.submit_button.click()

    def check_registration_is_successful(self):
        self.page.wait_for_url("**/login", timeout=10000)
        
        success_message = self.page.get_by_text("Подтвердите свою почту")
        expect(success_message).to_be_visible(timeout=5000)

    def check_error_message(self, message: str):
        error_locator = self.page.get_by_text(message)
        expect(error_locator.first).to_be_visible() 