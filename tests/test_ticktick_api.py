import pytest
from requests import HTTPError

from tickthon._ticktick_api import TicktickAPI


@pytest.fixture(scope="module")
def ticktick_api(ticktick_info):
    return TicktickAPI(ticktick_info["username"], ticktick_info["password"])


def test_login(ticktick_api, ticktick_info):
    token, cookies = ticktick_api._login(ticktick_info["username"], ticktick_info["password"])

    assert isinstance(token, str)
    assert token != ""
    assert token.isalnum()
    
    assert isinstance(cookies, dict)
    assert cookies != {}


def test_login_with_wrong_credentials(ticktick_api):
    with pytest.raises(HTTPError):
        ticktick_api._login("wrong-username", "wrong-password")


def test_get_request(ticktick_api):
    habits_url = ticktick_api.BASE_URL + "/habits"
    response = ticktick_api.get(habits_url)

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_request_with_wrong_url(ticktick_api):
    with pytest.raises(HTTPError):
        ticktick_api.get(ticktick_api.BASE_URL + "/task/a3b7c8d9e2f1a4b6c5d4e3f2")


def test_post_request(ticktick_api):
    habit_checkins_url = ticktick_api.BASE_URL + "/habitCheckins/query"
    payload = {"habitIds": ["test-request"], "afterStamp": 20230110}

    response = ticktick_api.post(habit_checkins_url, payload)

    assert response.status_code == 200
    assert isinstance(response.json(), dict)
