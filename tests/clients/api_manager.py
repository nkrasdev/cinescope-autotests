from tests.clients.auth_api import AuthAPI
from tests.clients.movies_api import MoviesAPI


class ApiManager:
    def __init__(self, session, base_url: str):
        self.session = session
        self.auth_api = AuthAPI(session)
        self.movies_api = MoviesAPI(session, base_url=base_url)

        self.movies_api.auth_handler = self.auth_api
