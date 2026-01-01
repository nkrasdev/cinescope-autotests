from tests.config import settings

BASE_URL = settings.base_url
BASE_UI_URL = settings.base_ui_url
BASE_AUTH_URL = settings.base_auth_url

HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

MOVIES_ENDPOINT = "/movies"
CREATE_MOVIE_ENDPOINT = "/movies"
MOVIE_BY_ID_ENDPOINT = "/movies/{movie_id}"

LOGIN_ENDPOINT = "/login"
REGISTER_ENDPOINT = "/register"
LOGOUT_ENDPOINT = "/logout"
REFRESH_ENDPOINT = "/refresh-tokens"

ADMIN_EMAIL = settings.admin_email
ADMIN_PASSWORD = settings.admin_password

NON_EXISTENT_ID = 999999999

CARD_NUMBER = "4242424242424242"
HOLDER_NAME = "Test User"
EXP_MONTH = "Декабрь"
EXP_YEAR = "2025"
CVC = "123"
