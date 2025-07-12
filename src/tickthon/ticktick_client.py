import logging
from datetime import datetime, timedelta, timezone


from ._ticktick_api import TicktickAPI
from .data.ticktick_payloads import TicktickPayloads
from .data.ticktick_ids import TicktickListIds
from .data.ticktick_list_parameters import TicktickListParameters as tlp
from .task_model import Task
from ._task_utils import _is_task_a_weight_measurement, _is_task_active, dict_to_task, parse_ticktick_tasks

current_date = datetime.now(timezone.utc)
date_two_weeks_ago = (current_date - timedelta(days=14)).strftime("%Y-%m-%d")
date_tomorrow = (current_date + timedelta(days=1)).strftime("%Y-%m-%d")


class TicktickClient:
    """Ticktick client."""
    BASE_URL = TicktickAPI.BASE_URL
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
    ACTIVE_FOCUS_TIME_URL = BASE_URL + "/pomodoros/statistics/dist"

    def __init__(self,
                 username: str,
                 password: str,
                 ticktick_list_ids: TicktickListIds,
                 api_token: str | None = None,
                 cookies: dict[str, str] | None = None):
        self.ticktick_api = TicktickAPI(username, password, api_token, cookies)
        self.ticktick_data: dict = {}
        self.ticktick_list_ids: TicktickListIds = ticktick_list_ids
        self._cached_raw_active_tasks: list[dict] = []
        self.all_active_tasks: list[Task] = []
        self.active_tasks: list[Task] = []
        self.completed_tasks: list[Task] = []
        self.deleted_tasks: list[Task] = []
        self.abandoned_tasks: list[Task] = []
        self.weight_measurements: list[Task] = []

        self._get_all_tasks()

    def _get_ticktick_data(self):
        """Gets raw data from Ticktick."""
        self.ticktick_data = self.ticktick_api.get(self.GET_STATE_URL).json()

    def _get_all_tasks(self):
        """Gets all tasks from Ticktick."""
        self._get_ticktick_data()

        raw_active_tasks = self.ticktick_data["syncTaskBean"]["update"]
        if raw_active_tasks == self._cached_raw_active_tasks:
            return

        self._cached_raw_active_tasks = raw_active_tasks
        self.all_active_tasks = parse_ticktick_tasks(raw_active_tasks, self.ticktick_list_ids.get_ids())

        self.active_tasks = []
        for task in self.all_active_tasks:
            if _is_task_a_weight_measurement(task, self.ticktick_list_ids):
                self.weight_measurements.append(task)
            elif _is_task_active(task):
                self.active_tasks.append(task)
            else:
                logging.warning(f"Task {task} does not have a valid status")

    def move_task_to_project(self, task: Task, project_id: str):
        """Moves a task from one project (list) to another in Ticktick.

        Args:
            task: Task to move.
            project_id: Project id to move the task to.
        """
        payload = TicktickPayloads.move_task_to_project(task, project_id)
        self.ticktick_api.post(self.MOVE_TASK_URL, data=payload)

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
        self.ticktick_api.post(self.CRUD_TASK_URL, data=payload)
        return True

    def get_active_tasks(self) -> list[Task]:
        """Gets all active tasks from Ticktick.

        Returns:
            Active tasks.
        """
        self._get_all_tasks()
        return self.active_tasks

    def get_completed_tasks(self) -> list[Task]:
        """Gets all completed tasks from Ticktick.

        Returns:
            Completed tasks.
        """
        logging.info("Getting completed tasks")

        self._get_ticktick_data()
        raw_completed_tasks = self.ticktick_api.get(self.COMPLETED_TASKS_URL).json()
        self.completed_tasks = parse_ticktick_tasks(raw_completed_tasks, self.ticktick_list_ids.get_ids())

        return self.completed_tasks

    def get_deleted_tasks(self) -> list[Task]:
        """Gets all deleted tasks from Ticktick.

        Returns:
            Deleted tasks.
        """
        self._get_ticktick_data()
        raw_deleted_tasks = self.ticktick_api.get(self.DELETED_TASKS_URL).json()["tasks"]
        self.deleted_tasks = parse_ticktick_tasks(raw_deleted_tasks, self.ticktick_list_ids.get_ids())

        return self.deleted_tasks

    def get_abandoned_tasks(self) -> list[Task]:
        """Gets all abandoned tasks from Ticktick.

        Returns:
            Abandoned tasks.
        """
        self._get_ticktick_data()
        raw_abandoned_tasks = self.ticktick_api.get(self.ABANDONED_TASKS_URL).json()
        self.abandoned_tasks = parse_ticktick_tasks(raw_abandoned_tasks, self.ticktick_list_ids.get_ids())

        return self.abandoned_tasks

    def get_task(self, task_id: str) -> Task:
        """Gets task information from Ticktick using the API.

        Args:
            task_id: Ticktick id of the task to get.

        Returns:
            Task or dictionary with the task information.
        """
        task = self.ticktick_api.get(f"{self.TASK_URL}/{task_id}").json()
        return dict_to_task(task)

    def complete_task(self, task: Task):
        """Completes a task in Ticktick using the API."""
        payload = TicktickPayloads.complete_task(task)
        self.ticktick_api.post(self.CRUD_TASK_URL, data=payload)

    def create_task(self, task: Task, column_id: str | None = None) -> str:
        """Creates a task in Ticktick using the API.

        Args:
            task: Task to create.
            column_id: Column id to create the task in. If it is set to None, the task is created in the default column.

        Returns:
            Ticktick id of the created task.
        """
        payload = TicktickPayloads.create_task(task, column_id)
        response = self.ticktick_api.post(self.CRUD_TASK_URL, payload).json()
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

    def get_active_focus_time(self, date: str, active_focus_tags: list[str]) -> float:
        """Gets the active focus time of a day from Ticktick.

        Args:
            date: Date to get the focus time from in the format YYYY-MM-DD.

        Returns:
            Active focus time.
        """
        clean_date = date.replace("-", "")
        raw_time = self.ticktick_api.get(f"{self.ACTIVE_FOCUS_TIME_URL}/{clean_date}/{clean_date}").json()
        tag_time = raw_time.get("tagDurations", {})

        active_focus_time = 0
        for tag in active_focus_tags:
            active_focus_time += tag_time.get(tag, 0)

        return round(active_focus_time / 60, 2)

    def get_tasks_by_list(self, list_ids: list[str]) -> list[Task]:
        """Gets all tasks from Ticktick by list ids.

        Args:
            list_ids: List ids to get the tasks from.

        Returns:
            Tasks.
        """
        self._get_all_tasks()
        return [task for task in self.all_active_tasks if task.project_id in list_ids]
