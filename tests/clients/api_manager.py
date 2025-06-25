from tests.clients.auth_api import AuthAPI
from tests.clients.movies_api import MoviesAPI
from tests.constants import BASE_URL, BASE_AUTH_URL

class ApiManager:
    def __init__(self, session, base_url: str = BASE_URL, base_auth_url: str = BASE_AUTH_URL):
        self.session = session
        self.auth_api = AuthAPI(session, base_url=base_auth_url)
        self.movies_api = MoviesAPI(session, base_url=base_url)

        self.movies_api.auth_handler = self.auth_api
