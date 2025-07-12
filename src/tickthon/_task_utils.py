from dateutil import parser, tz

from tickthon.data.ticktick_ids import TicktickListIds

from .data.ticktick_task_parameters import TicktickTaskParameters as ttp
from .task_model import Task


def parse_ticktick_tasks(raw_tasks: list[dict] | dict, valid_ticktick_lists_ids: list | None = None) \
        -> list[Task]:
    """Parses raw tasks from Ticktick into Task objects.

    Args:
        raw_tasks: Raw tasks from Ticktick.
        valid_ticktick_lists_ids: Ticktick lists ids to filter tasks by. If it is set to None, all tasks are parsed.

    Returns:
        Parsed tasks.
    """
    ticktick_tasks = []
    valid_ticktick_lists = valid_ticktick_lists_ids if valid_ticktick_lists_ids else []

    if not isinstance(raw_tasks, list):
        raw_tasks = [raw_tasks]

    for raw_task in raw_tasks:
        if valid_ticktick_lists and raw_task[ttp.PROJECT_ID.value] not in valid_ticktick_lists:
            continue

        ticktick_tasks.append(dict_to_task(raw_task))
    return ticktick_tasks


def dict_to_task(raw_task: dict) -> Task:
    """Converts a raw task to a Task object.

    Args:
        raw_task: The raw task as dictionary.

    Returns:
        A Task object.
    """
    return Task(ticktick_id=raw_task[ttp.ID.value],
                ticktick_etag=raw_task[ttp.ETAG.value],
                created_date=get_task_date(raw_task.get(ttp.TIMEZONE.value, ""),
                                           raw_task.get(ttp.CREATED_TIME.value, None)),
                status=raw_task[ttp.STATUS.value],
                title=raw_task[ttp.TITLE.value].strip(),
                focus_time=get_focus_time(raw_task),
                deleted=raw_task.get(ttp.DELETED.value, 0),
                tags=tuple(raw_task.get(ttp.TAGS.value, ())),
                project_id=raw_task[ttp.PROJECT_ID.value],
                timezone=raw_task[ttp.TIMEZONE.value],
                due_date=get_task_date(raw_task[ttp.TIMEZONE.value], raw_task.get(ttp.START_DATE.value, None)),
                column_id=raw_task.get(ttp.COLUMN_ID.value, ""),
                parent_id=raw_task.get(ttp.PARENT_ID.value, "")
                )


def get_focus_time(raw_task: dict) -> float:
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


def get_task_date(raw_task_timezone: str, task_date: str | None) -> str:
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


def _is_task_a_weight_measurement(task: Task, ticktick_ids: TicktickListIds) -> bool:
    """Checks if a task is a weight measurement."""
    weight_measurements_list_id = ticktick_ids.WEIGHT_MEASUREMENTS

    if weight_measurements_list_id is None:
        return False

    return task.project_id == weight_measurements_list_id


def _is_task_active(task: Task) -> bool:
    """Checks if a task is active."""
    return task.status == 0 and task.deleted == 0
