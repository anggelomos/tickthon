import os
import json
import warnings
from typing import Dict

CHECKINS_START_DATE = 20221231


def check_ticktick_ids() -> bool:
    """Checks if the Ticktick ids are set in the environment variables."""
    return os.getenv("TICKTICK_IDS") is not None


def get_ticktick_ids() -> Dict[str, Dict[str, str]]:
    if check_ticktick_ids():
        return json.loads(os.getenv("TICKTICK_IDS", default=""))
    warnings.warn("Environment variable TICKTICK_IDS is not set.")
    return {}
