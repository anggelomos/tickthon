import logging
import datetime
from typing import List, Optional, Tuple, Iterable

from . import ExpenseLog
from ._config import get_ticktick_ids, check_ticktick_ids
from ._ticktick_api import TicktickAPI
from .data.ticktick_payloads import TicktickPayloads
from .data.ticktick_id_keys import TicktickIdKeys as tik
from .data.ticktick_task_parameters import TicktickTaskParameters as ttp
from .data.ticktick_list_parameters import TicktickListParameters as tlp
from .task_model import Task
from ._task_utils import (_is_task_an_idea, _is_task_an_expense_log, _is_task_active,
                          dict_to_task, _parse_expense_log, _is_task_a_weight_measurement)

current_date = datetime.datetime.utcnow()
date_two_weeks_ago = (current_date - datetime.timedelta(days=14)).strftime("%Y-%m-%d")
date_tomorrow = (current_date + datetime.timedelta(days=1)).strftime("%Y-%m-%d")


class TicktickClient:
    """Ticktick client."""
    BASE_URL = "/api/v2"
    GET_STATE_URL = BASE_URL + "/batch/check/0"
    CRUD_TASK_URL = BASE_URL + "/batch/task"
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
        self.ideas: List[Task] = []
        self.weight_measurements: List[Task] = []
        self.expense_logs: List[Tuple[Task, ExpenseLog]] = []

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

        weight_measurements_id = None
        if get_ticktick_ids() is not None:
            weight_measurements_id = get_ticktick_ids()[tik.LIST_IDS.value].get("weight_measurements")

        for task in self.all_active_tasks:
            if _is_task_a_weight_measurement(task, weight_measurements_id):
                self.weight_measurements.append(task)
            elif _is_task_an_idea(task):
                self.ideas.append(task)
            elif _is_task_an_expense_log(task):
                expense_log = _parse_expense_log(task)
                if expense_log is not None:
                    self.expense_logs.append((task, expense_log))
            elif _is_task_active(task):
                self.active_tasks.append(task)
            else:
                logging.warning(f"Task {task} does not have a valid status")

    def get_ideas(self) -> List[Task]:
        """Gets all the tasks which title starts with "Idea:" from Ticktick.

        Returns:
            Ideas.
        """
        self._get_all_tasks()
        return self.ideas

    def get_expense_logs(self) -> List[Tuple[Task, ExpenseLog]]:
        """Gets all the tasks which title starts with "$" from Ticktick.

        Returns:
            Expense logs.
        """
        self._get_all_tasks()
        return self.expense_logs

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
        payload = TicktickPayloads.complete_task(task.ticktick_id, task.project_id)
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
