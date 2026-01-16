from tests.config import settings

BASE_URL = settings.base_url
BASE_UI_URL = settings.base_ui_url
BASE_AUTH_URL = settings.base_auth_url
BASE_PAYMENT_URL = settings.base_payment_url

HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

MOVIES_ENDPOINT = "/movies"
CREATE_MOVIE_ENDPOINT = "/movies"
MOVIE_BY_ID_ENDPOINT = "/movies/{movie_id}"
REVIEWS_ENDPOINT = "/movies/{movie_id}/reviews"
REVIEW_HIDE_ENDPOINT = "/movies/{movie_id}/reviews/hide/{user_id}"
REVIEW_SHOW_ENDPOINT = "/movies/{movie_id}/reviews/show/{user_id}"

LOGIN_ENDPOINT = "/login"
REGISTER_ENDPOINT = "/register"
LOGOUT_ENDPOINT = "/logout"
REFRESH_ENDPOINT = "/refresh-tokens"
CONFIRM_ENDPOINT = "/confirm"

USERS_ENDPOINT = "/user"
USER_BY_ID_ENDPOINT = "/user/{user_id}"
USER_BY_ID_OR_EMAIL_ENDPOINT = "/user/{id_or_email}"

PAYMENT_CREATE_ENDPOINT = "/create"
PAYMENT_USER_ENDPOINT = "/user"
PAYMENT_USER_BY_ID_ENDPOINT = "/user/{user_id}"
PAYMENT_FIND_ALL_ENDPOINT = "/find-all"

GENRES_ENDPOINT = "/genres"
GENRE_BY_ID_ENDPOINT = "/genres/{genre_id}"

ADMIN_EMAIL = settings.admin_email
ADMIN_PASSWORD = settings.admin_password

NON_EXISTENT_ID = 999999999
