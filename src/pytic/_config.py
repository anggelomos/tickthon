import os
import json

CHECKINS_START_DATE = 20221231


def get_ticktick_ids():
    return json.loads(os.getenv("TICKTICK_IDS", default="")) if os.getenv("TICKTICK_IDS") else None
