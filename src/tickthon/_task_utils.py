import re
from datetime import datetime
from typing import List, Optional
from dateutil import parser, tz

from . import ExpenseLog
from ._config import get_ticktick_ids
from .data.day_log_words import PAST_TENSE_VERBS, LOG_EXCEPTION_WORDS
from .data.ticktick_task_parameters import TicktickTaskParameters as ttp
from .data.ticktick_id_keys import TicktickIdKeys as tik, TicktickFolderKeys as tfK
from .task_model import Task


def _clean_habit_checkins(checkins: List[dict]) -> List[str]:
    """Returns a list of formatted dates from successful habit checkins.

        Args:
            checkins (List[dict]): A list of checkin dictionaries with "checkinStamp" and "status".


        Returns:
            List[str]: A list of strings representing dates of successful checkins ('YYYY-MM-DD').
                       Returns an empty list if no successful checkins are found.

        Example:
            >>> _clean_habit_checkins([{"checkinStamp": "20230925", "status": 2}])
            ['2023-09-25']
    """
    if not checkins:
        return []

    def parse_date(date: str) -> str:
        return datetime.strptime(str(date), '%Y%m%d').strftime('%Y-%m-%d')

    return [parse_date(checkin["checkinStamp"]) for checkin in checkins if checkin["status"] == 2]


def _is_task_a_weight_measurement(task: Task) -> bool:
    """Checks if a task is a weight measurement."""
    weight_measurements_list_id = None
    ticktick_ids = get_ticktick_ids()
    if ticktick_ids is not None:
        weight_measurements_list_id = get_ticktick_ids()[tik.LIST_IDS.value].get(tfK.WEIGHT_MEASUREMENTS.value)

    if weight_measurements_list_id is None:
        return False

    return task.project_id == weight_measurements_list_id


def _is_task_an_expense_log(task: Task) -> bool:
    """Checks if a task is an expense log."""
    return task.title.startswith("$")


def _is_task_day_log(task: Task) -> bool:
    """Checks if a task is a day log."""
    day_logs_list_id = ""
    ticktick_ids = get_ticktick_ids()
    if ticktick_ids is not None:
        day_logs_list_id = get_ticktick_ids()[tik.LIST_IDS.value].get(tfK.DAY_LOGS.value, "")

    if task.project_id == day_logs_list_id:
        return True

    if task.project_id == get_ticktick_ids()[tik.LIST_IDS.value].get(tfK.INBOX_TASKS.value):
        if task.title.lower().startswith(("i ", "i'm ", "i'll ", "im ", "ill ")):
            return True

        title_first_word = task.title.split()[0].lower()
        if (title_first_word not in LOG_EXCEPTION_WORDS and
                (title_first_word.endswith("ed") or
                 title_first_word.endswith("ing") or
                 title_first_word in PAST_TENSE_VERBS)):
            return True

    return task.project_id == day_logs_list_id


def _is_day_log_a_highlight(task: Task) -> bool:
    """Checks if a day log is a highlight."""
    return "highlight" in task.tags


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
                ticktick_etag=raw_task[ttp.ETAG.value],
                created_date=_get_task_date(raw_task[ttp.TIMEZONE.value], raw_task.get(ttp.CREATED_TIME.value, None)),
                status=raw_task[ttp.STATUS.value],
                title=raw_task[ttp.TITLE.value].strip(),
                focus_time=_get_focus_time(raw_task),
                deleted=raw_task.get(ttp.DELETED.value, 0),
                tags=tuple(raw_task.get(ttp.TAGS.value, ())),
                project_id=raw_task[ttp.PROJECT_ID.value],
                timezone=raw_task[ttp.TIMEZONE.value],
                due_date=_get_task_date(raw_task[ttp.TIMEZONE.value], raw_task.get(ttp.START_DATE.value, None)),
                column_id=raw_task.get(ttp.COLUMN_ID.value, "")
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


def _get_task_date(raw_task_timezone: str, task_date: str) -> str:
    """Returns the date of a task taking into account the timezone.

    Args:
        raw_task_timezone: The timezone of the task.
        task_date: The start date of the task.

    Returns:
        Task's date in iso format YYYY-MM-DDTHH:MM:SS+0000., if the task has no start date, returns an empty string.
    """
    if not task_date:
        return ""

    task_timezone = tz.gettz(raw_task_timezone)
    task_raw_date = parser.parse(task_date)

    localized_task_date = task_raw_date.astimezone(task_timezone)
    task_date = localized_task_date.isoformat()

    return task_date


def _parse_expense_log(raw_expense_logs: Task) -> Optional[ExpenseLog]:
    """Parses raw expense logs from Ticktick into ExpenseLog objects.

    Args:
        raw_expense_logs: Raw expense logs from Ticktick.

    Returns:
        Parsed expense logs.
    """
    expense_parse = re.search(r"\$([\d\.]+)\s+(.+)", raw_expense_logs.title)
    if not expense_parse:
        return None

    date = raw_expense_logs.due_date
    if not date:
        date = datetime.now(tz.gettz(raw_expense_logs.timezone)).strftime("%Y-%m-%d")

    return ExpenseLog(date=date,
                      expense=float(expense_parse.group(1)),
                      product=expense_parse.group(2))
