from enum import Enum

from requests import Session, Response


class RequestTypes(Enum):
    """Types of requests that can be sent to the Ticktick API."""
    GET = "GET"
    POST = "POST"


class TicktickAPI:
    """Ticktick API client."""
    BASE_URL = "https://api.ticktick.com/api/v2"
    SIGNIN_URL = BASE_URL + "/user/signon?wc=true&remember=true"

    USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:95.0) Gecko/20100101 Firefox/95.0'
    X_DEVICE_ = '{"platform":"web","os":"Windows 10","device":"Chrome 123.0.0.0","name":"","version":5303,"id":"65f10b61131d8a5bf9e68825","channel":"website","campaign":"","websocket":""}'  # noqa: E501

    SIGNIN_HEADERS = {'User-Agent': USER_AGENT,
                      'x-device': X_DEVICE_,
                      'Content-Type': 'application/json'}

    def __init__(self, username: str,
                 password: str,
                 api_token: str | None = None,
                 cookies: dict[str, str] | None = None):
        self.session = Session()
        self.session.headers.update({"Content-Type": "application/json",
                                     "User-Agent": self.USER_AGENT,
                                     "x-device": self.X_DEVICE_
                                     })

        self.auth_token, self.cookies = self.validate_token(username, password, api_token, cookies)

    def _login(self, user: str, password: str) -> tuple[str, dict[str, str]]:
        """Logs into Ticktick and returns the authentication token.

        Args:
            user: Ticktick username
            password: Ticktick password

        Returns:
            A tuple with the token and the cookie.
        """
        payload = {"username": user, "password": password}
        response = self.session.post(self.SIGNIN_URL, headers=self.SIGNIN_HEADERS, json=payload)
        response.raise_for_status()

        cookies = {name: value for name, value in self.session.cookies.items()}

        return response.json()["token"], cookies

    def validate_token(self,
                       username: str,
                       password: str,
                       api_token: str | None,
                       cookies: dict[str, str] | None) -> tuple[str, dict[str, str]]:
        """Validate the token. If the token is invalid, login again.

        Args:
            username: The username to login with.
            password: The password to login with.
            api_token: The api token to validate.
            cookies: The cookies to use for the request.

        Returns:
            A tuple with the token and refresh token.
        """
        self.session.headers.update({"Authorization": f"Bearer {api_token}"})

        if cookies:
            self.session.cookies.update(cookies)

        current_token_response = self.session.get(self.BASE_URL + "/batch/check/0")

        if current_token_response.ok and cookies and api_token:
            return api_token, cookies

        return self._login(username, password)

    def post(self, url: str, data: dict | list | None = None) -> Response:
        """Sends a POST request to the Ticktick API.

        Args:
            url: URL to send the request to
            data: Data to send in the request. Defaults to None.

        Returns:
            Response from the Ticktick API
        """

        response = self.session.post(url, json=data)
        response.raise_for_status()

        return response

    def get(self, url: str, data: dict | list | None = None) -> Response:
        """Sends a GET request to the Ticktick API.

        Args:
            url: URL to send the request to
            data: Data to send in the request. Defaults to None.

        Returns:
            Response from the Ticktick API
        """

        response = self.session.get(url, json=data)
        response.raise_for_status()

        return response
