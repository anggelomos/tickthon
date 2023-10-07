from typing import Optional, List

from attrs import define, field


@define(frozen=True)
class Task:
    """ Represents a Ticktick task.

    Attributes:
        title: The title of the task.
        status: The status of the task. 0: default/open, 2: done, -1: abandoned.
        ticktick_id: The ID of the task. For example: 6f8a2b3c4d5e1f09a7b6c8d9e0f2
        focus_time: The focus time of the task.
        deleted: The status of the task. 0: not deleted, 1: deleted.
        tags: The tags of the task as a list of strings.
        project_id: The ID of the project of the task. For example: 6f8a2b3c4d5e1f09a7b6c8d9e0f2
        timezone: The timezone of the task.
        due_date: The due date of the task in format YYYY-MM-DD.
        recurrent_id (Optional[str]): The ID of the recurrent task.  For example: 6f8a2b3c4d5e1f09a7b6c8d9e0f2
    """
    title: str
    status: int = 0
    ticktick_id: str = field(default="", eq=str.lower)
    focus_time: float = 0
    deleted: int = 0
    tags: List[str] = []
    project_id: str = field(default="", eq=str.lower)
    timezone: str = field(default="", eq=str.lower)
    due_date: str = field(default="", eq=str.lower)
    recurrent_id: Optional[str] = ""
