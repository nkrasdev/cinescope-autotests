import time
from urllib.parse import urljoin

import requests

from tests.constants import MOVIES_ENDPOINT, CREATE_MOVIE_ENDPOINT, MOVIE_BY_ID_ENDPOINT
from tests.request.custom_requester import CustomRequester

class MoviesAPI(CustomRequester):
    def __init__(self, session: requests.Session, base_url: str):
        super().__init__(session, base_url)

    def create_movie(self, movie_data: dict, *, expected_status: int = 201):
        return self.send_request("POST",
                                 CREATE_MOVIE_ENDPOINT,
                                 data=movie_data,
                                 expected_status=expected_status)

    def get_movie_by_id(self, movie_id: int, *, expected_status: int = 200):
        return self.send_request("GET",
                                 MOVIE_BY_ID_ENDPOINT.format(movie_id=movie_id),
                                 expected_status=expected_status)

    def delete_movie(self, movie_id, *, expected_status: int = 200):
        return self.send_request("DELETE",
                                 MOVIE_BY_ID_ENDPOINT.format(movie_id=movie_id),
                                 expected_status=expected_status)

    def get_movies(self, params: dict | None = None, *, expected_status: int = 200):
        request_params = params.copy() if params else {}
        if "published" in request_params:
            request_params["published"] = str(request_params["published"]).lower()

        return self.send_request("GET",
                                 MOVIES_ENDPOINT,
                                 data=request_params,
                                 expected_status=expected_status)

    def get_movies_with_invalid_params(self, *, params: dict, expected_status: int = 400):
        return self.send_request("GET",
                                 MOVIES_ENDPOINT,
                                 data=params,
                                 expected_status=expected_status)

    def edit_movie(self, movie_id, payload: dict, *, expected_status: int = 200):
        return self.send_request("PATCH",
                                 MOVIE_BY_ID_ENDPOINT.format(movie_id=movie_id),
                                 data=payload,
                                 expected_status=expected_status)