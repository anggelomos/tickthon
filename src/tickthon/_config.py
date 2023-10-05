import os
import json
from typing import Dict

CHECKINS_START_DATE = 20221231


def get_ticktick_ids() -> Dict[str, str]:
    return json.loads(os.getenv("TICKTICK_IDS", default="")) if os.getenv("TICKTICK_IDS") else None
