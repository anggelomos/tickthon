import logging
from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Iterable

from dateutil.tz import tz

from . import ExpenseLog
from ._config import get_ticktick_ids, check_ticktick_ids
from ._ticktick_api import TicktickAPI
from .data.ticktick_payloads import TicktickPayloads
from .data.ticktick_id_keys import TicktickIdKeys as tik, TicktickFolderKeys as tfK
from .data.ticktick_task_parameters import TicktickTaskParameters as ttp
from .data.ticktick_list_parameters import TicktickListParameters as tlp
from .task_model import Task
from ._task_utils import (_is_task_an_expense_log, _is_task_active,
                          dict_to_task, _parse_expense_log, _is_task_day_log, _is_day_log_a_highlight)

current_date = datetime.utcnow()
date_two_weeks_ago = (current_date - timedelta(days=14)).strftime("%Y-%m-%d")
date_tomorrow = (current_date + timedelta(days=1)).strftime("%Y-%m-%d")


class TicktickClient:
    """Ticktick client."""
    BASE_URL = "/api/v2"
    GET_STATE_URL = BASE_URL + "/batch/check/0"
    CRUD_TASK_URL = BASE_URL + "/batch/task"
    MOVE_TASK_URL = BASE_URL + "/batch/taskProject"
    TASK_URL = BASE_URL + "/task"
    HABIT_CHECKINS_URL = BASE_URL + "/habitCheckins/query"
    COMPLETED_TASKS_URL = BASE_URL + f"/project/all/closed?from={date_two_weeks_ago}%2005:00:00&to={date_tomorrow}" \
                                     f"%2004:59:00&status=Completed&limit=500"
    ABANDONED_TASKS_URL = BASE_URL + f"/project/all/closed?from={date_two_weeks_ago}%2005:00:00&to={date_tomorrow}" \
                                     f"%2004:59:00&status=Abandoned&limit=500"
    DELETED_TASKS_URL = BASE_URL + "/project/all/trash/pagination?start=0&limit=500"
    GENERAL_FOCUS_TIME_URL = BASE_URL + "/pomodoros/statistics/heatmap"

    def __init__(self, username: str, password: str):
        self.ticktick_api = TicktickAPI(username, password)
        self.ticktick_data: dict = {}
        self.project_lists: List[str] = []
        self._cached_raw_active_tasks: List[dict] = []
        self.all_active_tasks: List[Task] = []
        self.active_tasks: List[Task] = []
        self.completed_tasks: List[Task] = []
        self.deleted_tasks: List[Task] = []
        self.abandoned_tasks: List[Task] = []
        self.weight_measurements: List[Task] = []
        self.expense_logs: List[Tuple[Task, ExpenseLog]] = []
        self.all_day_logs: List[Task] = []
        self.day_logs: List[Task] = []

        self._get_all_tasks()

    @staticmethod
    def _parse_ticktick_tasks(raw_tasks: List[dict] | dict, valid_ticktick_lists_ids: Optional[list] = None) \
            -> List[Task]:
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

        if check_ticktick_ids() and get_ticktick_ids().get(tik.LIST_IDS.value, False):
            valid_ticktick_lists += get_ticktick_ids()[tik.LIST_IDS.value].values()

        for raw_task in raw_tasks:
            if valid_ticktick_lists and raw_task[ttp.PROJECT_ID.value] not in valid_ticktick_lists:
                continue

            ticktick_tasks.append(dict_to_task(raw_task))
        return ticktick_tasks

    @staticmethod
    def _get_folder_lists(lists: List[dict]) -> Optional[dict]:
        """Gets all folder lists from Ticktick.

        Args:
            lists: Raw lists from Ticktick.

        Returns:
            Project lists with this format {list_id: list_name}.
        """
        folder_lists = {}
        folder_ids: Iterable[str] = []
        if check_ticktick_ids() and get_ticktick_ids().get(tik.FOLDER_IDS.value, False):
            folder_ids = get_ticktick_ids()[tik.FOLDER_IDS.value].values()
        if folder_ids:
            folder_lists = {project_list[tlp.NAME]: project_list[tlp.ID] for project_list in lists
                            if project_list[tlp.GROUP_ID] in folder_ids}

        return folder_lists

    def _get_ticktick_data(self):
        """Gets raw data from Ticktick."""
        self.ticktick_data = self.ticktick_api.get(self.GET_STATE_URL).json()
        self.project_lists = list(self._get_folder_lists(self.ticktick_data["projectProfiles"]).values())

    def _get_all_tasks(self):
        """Gets all tasks from Ticktick."""
        self._get_ticktick_data()

        raw_active_tasks = self.ticktick_data["syncTaskBean"]["update"]
        if raw_active_tasks == self._cached_raw_active_tasks:
            return

        self._cached_raw_active_tasks = raw_active_tasks
        self.all_active_tasks = self._parse_ticktick_tasks(raw_active_tasks, self.project_lists)

        self.all_day_logs = []
        self.expense_logs = []
        self.active_tasks = []
        for task in self.all_active_tasks:
            # TODO: Add weight measurements once they are restored
            # if _is_task_a_weight_measurement(task):
            #     self.weight_measurements.append(task)
            if _is_task_day_log(task):
                self.all_day_logs.append(task)
            elif _is_task_an_expense_log(task):
                expense_log = _parse_expense_log(task)
                if expense_log is not None:
                    self.expense_logs.append((task, expense_log))
            elif _is_task_active(task):
                self.active_tasks.append(task)
            else:
                logging.warning(f"Task {task} does not have a valid status")

    def get_expense_logs(self) -> List[Tuple[Task, ExpenseLog]]:
        """Gets all the tasks which title starts with "$" from Ticktick.

        Returns:
            Expense logs.
        """
        self._get_all_tasks()
        return self.expense_logs

    def move_task_to_project(self, task: Task, project_id: str):
        payload = TicktickPayloads.move_task_to_project(task, project_id)
        self.ticktick_api.post(self.MOVE_TASK_URL, data=payload, token_required=True)

    def replace_task_tags(self, task: Task, tags: tuple[str, ...]) -> bool:
        """Replaces the tags of a task in Ticktick.

        Args:
            task: Task to replace the tags.
            tags: Tags to replace the task tags with.

        Returns:
            True if the tags were replaced successfully, False otherwise.
        """
        self._get_all_tasks()
        tasks_raw_data = [rt for rt in self._cached_raw_active_tasks if rt[tlp.ID] == task.ticktick_id]

        if not tasks_raw_data:
            return False

        task_raw_data = tasks_raw_data[0]
        task_raw_data[tlp.TAGS] = tags
        payload = {"update": [task_raw_data]}
        self.ticktick_api.post(self.CRUD_TASK_URL, data=payload, token_required=True)
        return True

    def _replace_tags_in_highlight_log(self, task: Task, tags: tuple[str, ...] | None = None):
        task_tags = ("highlight",) if _is_day_log_a_highlight(task) else tuple()
        if tags:
            task_tags += tags

        self.replace_task_tags(task, task_tags)

    def _add_day_log_tags(self, task: Task, task_created_date: datetime, current_date_localized: datetime):
        if task_created_date >= current_date_localized and "today-log" not in task.tags:
            self._replace_tags_in_highlight_log(task, ("today-log",))
        elif current_date_localized > task_created_date >= (current_date_localized - timedelta(days=1)) and \
                "yesterday-log" not in task.tags:
            self._replace_tags_in_highlight_log(task, ("yesterday-log",))
        elif task_created_date < (current_date_localized - timedelta(days=1)) and len(task.tags) > 0:
            self._replace_tags_in_highlight_log(task)

    def _process_daily_logs(self):
        """Processes the daily logs."""
        self._get_all_tasks()

        for task in self.all_day_logs.copy():
            if task.project_id == get_ticktick_ids()[tik.LIST_IDS.value][tfK.INBOX_TASKS.value]:
                self._replace_tags_in_highlight_log(task)
                self.move_task_to_project(task, get_ticktick_ids()[tik.LIST_IDS.value][tfK.DAY_LOGS.value])
                continue

            task_created_date = datetime.fromisoformat(task.created_date)
            current_date_localized = datetime.now(tz.gettz(task.timezone)).replace(hour=0, minute=0, second=0,
                                                                                   microsecond=0)
            if task_created_date < (current_date_localized - timedelta(days=3)):
                self.complete_task(task)
                continue

            self._add_day_log_tags(task, task_created_date, current_date_localized)

            self.day_logs.append(task)

    def get_day_logs(self) -> List[Task]:
        """Gets all the day logs from Ticktick."""
        self._process_daily_logs()
        return self.day_logs

    def get_active_tasks(self) -> List[Task]:
        """Gets all active tasks from Ticktick.

        Returns:
            Active tasks.
        """
        self._get_all_tasks()
        return self.active_tasks

    def get_completed_tasks(self) -> List[Task]:
        """Gets all completed tasks from Ticktick.

        Returns:
            Completed tasks.
        """
        logging.info("Getting completed tasks")

        self._get_ticktick_data()
        raw_completed_tasks = self.ticktick_api.get(self.COMPLETED_TASKS_URL).json()
        self.completed_tasks = self._parse_ticktick_tasks(raw_completed_tasks, self.project_lists)

        return self.completed_tasks

    def get_deleted_tasks(self) -> List[Task]:
        """Gets all deleted tasks from Ticktick.

        Returns:
            Deleted tasks.
        """
        self._get_ticktick_data()
        raw_deleted_tasks = self.ticktick_api.get(self.DELETED_TASKS_URL).json()["tasks"]
        self.deleted_tasks = self._parse_ticktick_tasks(raw_deleted_tasks, self.project_lists)

        return self.deleted_tasks

    def get_abandoned_tasks(self) -> List[Task]:
        """Gets all abandoned tasks from Ticktick.

        Returns:
            Abandoned tasks.
        """
        self._get_ticktick_data()
        raw_abandoned_tasks = self.ticktick_api.get(self.ABANDONED_TASKS_URL).json()
        self.abandoned_tasks = self._parse_ticktick_tasks(raw_abandoned_tasks, self.project_lists)

        return self.abandoned_tasks

    def get_task(self, task_id: str) -> Task:
        """Gets task information from Ticktick using the API.

        Args:
            task_id: Ticktick id of the task to get.

        Returns:
            Task or dictionary with the task information.
        """
        task = self.ticktick_api.get(f"{self.TASK_URL}/{task_id}", token_required=True).json()
        return dict_to_task(task)

    def complete_task(self, task: Task):
        """Completes a task in Ticktick using the API."""
        payload = TicktickPayloads.complete_task(task)
        self.ticktick_api.post(self.CRUD_TASK_URL, data=payload, token_required=True)

    def create_task(self, task: Task, column_id: Optional[str] = None) -> str:
        """Creates a task in Ticktick using the API.

        Args:
            task: Task to create.
            column_id: Column id to create the task in. If it is set to None, the task is created in the default column.

        Returns:
            Ticktick id of the created task.
        """
        payload = TicktickPayloads.create_task(task, column_id)
        response = self.ticktick_api.post(self.CRUD_TASK_URL, payload, token_required=True).json()
        return list(response["id2etag"].keys())[0]

    def get_overall_focus_time(self, date: str) -> float:
        """Gets the overall focus time of a day from Ticktick.

        Args:
            date: Date to get the focus time from in the format YYYY-MM-DD.

        Returns:
            General focus time.
        """
        clean_date = date.replace("-", "")
        raw_time = self.ticktick_api.get(f"{self.GENERAL_FOCUS_TIME_URL}/{clean_date}/{clean_date}").json()

        return round(raw_time[0]["duration"] / 60, 2)
