from enum import Enum
from typing import Optional
import secrets

import requests
from requests import Response, HTTPError


class RequestTypes(Enum):
    """Types of requests that can be sent to the Ticktick API."""
    GET = "GET"
    POST = "POST"


class TicktickAPI:
    """Ticktick API client."""
    HOST = "https://api.ticktick.com"
    BASE_URL = "/api/v2"
    SIGNIN_URL = BASE_URL + "/user/signin?wc=True&remember=True"

    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:95.0) Gecko/20100101 Firefox/95.0"
    X_DEVICE_ = '{"platform":"web","os":"OS X","device":"Firefox 95.0","name":"unofficial api!","version":4531,' \
                '"id":"6490' + secrets.token_hex(10) + '","channel":"website","campaign":"","websocket":""}'

    HEADERS = {'User-Agent': USER_AGENT,
               'x-device': X_DEVICE_}

    def __init__(self, username: str, password: str):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json",
                                     "User-Agent": self.USER_AGENT,
                                     "x-device": self.X_DEVICE_
                                     })
        self.auth_token = self.login(username, password)

    def login(self, user: str, password: str) -> str:
        """Logs into Ticktick and returns the authentication token.

        Args:
            user: Ticktick username
            password: Ticktick password

        Returns:
            Ticktick authentication token
        """
        payload = {
            "username": user,
            "password": password
        }

        response = self.post(self.SIGNIN_URL, data=payload, token_required=False)

        if response.status_code != 200:
            raise HTTPError("Failed to login using the API "
                            f"Request status code: {response.status_code}, "
                            f"Request message: {response.text}")

        return response.json()["token"]

    def _base_request(self, request_type: RequestTypes, url: str, data: Optional[dict] = None,
                      token_required: bool = True) -> Response:
        """Sends a request to the Ticktick API.

        Args:
            request_type: Type of request to send
            url: URL to send the request to
            data: Data to send in the request. Defaults to None.
            token_required: Whether the request requires an authentication token. Defaults to True.

        Returns:
            Response from the Ticktick API
        """
        if token_required:
            self.session.headers.update({
                "Authorization": f"Bearer {self.auth_token}",
                "Cookie": f"t={self.auth_token}"
            })

        return self.session.request(request_type.value, f"{self.HOST}{url}", json=data)

    def post(self, url: str, data: Optional[dict] = None, token_required: bool = True) -> Response:
        """Sends a POST request to the Ticktick API.

        Args:
            url: URL to send the request to
            data: Data to send in the request. Defaults to None.
            token_required: Whether the request requires an authentication token. Defaults to True.

        Returns:
            Response from the Ticktick API
        """

        response = self._base_request(RequestTypes.POST, url, data, token_required)
        return response

    def get(self, url: str, data: Optional[dict] = None, token_required: bool = True) \
            -> Response:
        """Sends a GET request to the Ticktick API.

        Args:
            url: URL to send the request to
            data: Data to send in the request. Defaults to None.
            token_required: Whether the request requires an authentication token. Defaults to True.

        Returns:
            Response from the Ticktick API
        """

        response = self._base_request(RequestTypes.GET, url, data, token_required)

        if response.status_code != 200:
            raise HTTPError(f"Failed send get request using the API. "
                            f"Request status code: {response.status_code}, "
                            f"Request message: {response.text}")

        return response
