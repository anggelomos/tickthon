from datetime import datetime
from typing import List
from dateutil import parser, tz

from ._config import get_ticktick_ids
from .data.ticktick_id_keys import TicktickIdKeys as tik
from .data.ticktick_task_parameters import TicktickTaskParameters as ttp
from .task_model import Task


def _clean_habit_checkins(checkins: List[dict]) -> List[str]:
    if not checkins:
        return []

    def parse_date(date: str) -> str:
        return datetime.strptime(str(date), '%Y%m%d').strftime('%Y-%m-%d')

    return [parse_date(checkin["checkinStamp"]) for checkin in checkins if checkin["status"] == 2]


def _is_task_an_idea(task: Task) -> bool:
    """Checks if a task is an idea."""
    return task.title.startswith("Idea:")


def _is_task_an_expense_log(task: Task) -> bool:
    """Checks if a task is an expense log."""
    return task.title.startswith("$")


def _is_task_active(task: Task) -> bool:
    """Checks if a task is active."""
    return task.status == 0 and task.deleted == 0


def _is_task_completed(task: Task) -> bool:
    """Checks if a task is completed."""
    return task.status == 2


def _is_task_abandoned(task: Task) -> bool:
    """Checks if a task is abandoned."""
    return task.status == -1


def _is_task_deleted(task: Task) -> bool:
    """Checks if a task is deleted."""
    return task.deleted == 1


def dict_to_task(raw_task: dict) -> Task:
    """Converts a raw task to a Task object.

    Args:
        raw_task: The raw task as dictionary.

    Returns:
        A Task object.
    """
    return Task(ticktick_id=raw_task[ttp.ID.value],
                status=raw_task[ttp.STATUS.value],
                title=raw_task[ttp.TITLE.value].strip(),
                focus_time=_get_focus_time(raw_task),
                deleted=raw_task.get(ttp.DELETED.value, 0),
                tags=raw_task.get(ttp.TAGS.value, []),
                project_id=raw_task[ttp.PROJECT_ID.value],
                timezone=raw_task[ttp.TIMEZONE.value],
                due_date=_get_task_date(raw_task[ttp.TIMEZONE.value], raw_task.get(ttp.START_DATE.value, None)),
                kanban_status=_get_kanban_status(raw_task.get(ttp.COLUMN_ID.value, "")),
                recurrent_id=raw_task.get(ttp.REPEAT_TASK_ID.value, ""),
                )


def _get_focus_time(raw_task: dict) -> float:
    """Returns the focus time of a task.

    Args:
        raw_task: The raw task from Ticktick.

    Returns:
        The focus time of the task.
    """
    focus_time = 0.0
    if ttp.FOCUS_SUMMARIES.value in raw_task:
        raw_focus_time = map(lambda summary: summary[ttp.POMO_DURATION.value] + summary[ttp.STOPWATCH_DURATION.value],
                             raw_task[ttp.FOCUS_SUMMARIES.value])
        focus_time = round(sum(raw_focus_time) / 3600, 2)
    elif ttp.FOCUS_TIME.value in raw_task:
        focus_time = float(raw_task[ttp.FOCUS_TIME.value])

    return focus_time


def _get_task_date(timezone: str, start_date: str) -> str:
    if not start_date:
        return ""

    task_timezone = tz.gettz(timezone)

    task_raw_date = parser.parse(start_date)

    localized_task_date = task_raw_date.astimezone(task_timezone)
    task_date = localized_task_date.strftime("%Y-%m-%d")

    return task_date


def _get_kanban_status(column_id: str) -> str:
    """Returns the kanban status of a task.

    Args:
        column_id: The id of the column.

    Returns:
        The kanban status of the task.
    """
    kanban_status = ""
    if column_id and get_ticktick_ids() and get_ticktick_ids().get(tik.COLUMN_TAGS.value, False):
        kanban_status = get_ticktick_ids()[tik.COLUMN_TAGS.value].get(column_id, "")

    return kanban_status
