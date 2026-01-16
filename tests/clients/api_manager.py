from tests.clients.auth_api import AuthAPI
from tests.clients.movies_api import MoviesAPI
from tests.clients.payment_api import PaymentAPI
from tests.clients.users_api import UsersAPI
from tests.constants.endpoints import BASE_AUTH_URL, BASE_PAYMENT_URL, BASE_URL


class ApiManager:
    def __init__(
        self,
        session,
        base_url: str = BASE_URL,
        base_auth_url: str = BASE_AUTH_URL,
        base_payment_url: str = BASE_PAYMENT_URL,
    ):
        self.session = session
        self.auth_api = AuthAPI(session, base_url=base_auth_url)
        self.users_api = UsersAPI(session, base_url=base_auth_url)
        self.movies_api = MoviesAPI(session, base_url=base_url)
        self.payment_api = PaymentAPI(session, base_url=base_payment_url)
        self.movies_api.auth_handler = self.auth_api
