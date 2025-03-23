import json
import os
from pathlib import Path

import pytest

from tickthon.data.ticktick_ids import TicktickListIds


@pytest.fixture(scope="module")
def ticktick_info():
    return {
            "username": os.getenv("TT_USER"), 
            "password": os.getenv("TT_PASS"),
            "ticktick_ids": TicktickListIds(
                INBOX="inbox114478622",
                TODAY_BACKLOG="6616e1af8f08b66b69c7a5c5",
                WEEK_BACKLOG="61c62f198f08c92d0584f678",
                MONTH_BACKLOG="61c634f58f08c92d058540ba",
                WEIGHT_MEASUREMENTS="640c03cd8f08d5a6c4bb32e7"
            )
            }


@pytest.fixture(scope="session")
def test_folder_path():
    return Path(__file__).parent


@pytest.fixture(scope="session")
def data_folder_path(test_folder_path):
    return test_folder_path / "data"


@pytest.fixture(scope="session", autouse=True)
def set_test_ticktick_ids(data_folder_path):
    current_ticktick_ids = os.getenv("TICKTICK_IDS", "")

    with open(data_folder_path / "test_ticktick_ids.json", "r") as file:
        test_ticktick_ids = str(json.load(file)).replace("'", '"')
        os.environ["TICKTICK_IDS"] = test_ticktick_ids

    yield

    os.environ["TICKTICK_IDS"] = current_ticktick_ids


@pytest.fixture
def set_empty_test_ticktick_ids(data_folder_path):
    current_ticktick_ids = os.getenv("TICKTICK_IDS", "")
    os.environ["TICKTICK_IDS"] = ""
    yield
    os.environ["TICKTICK_IDS"] = current_ticktick_ids


@pytest.fixture(scope="session")
def dict_task(data_folder_path):
    with open(data_folder_path / "dict_task.json", "r") as file:
        return json.load(file)
