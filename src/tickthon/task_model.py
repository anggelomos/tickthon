from typing import Tuple

from attrs import define, field


@define
class Task:
    """ Represents a Ticktick task.

    Attributes:
        title: The title of the task.
        status: The status of the task. 0: default/open, 2: done, -1: abandoned.
        ticktick_id: The ID of the task. For example: 6f8a2b3c4d5e1f09a7b6c8d9e0f2
        ticktick_etag: The unique identifier for each task. For example: 4b7n9t2q
        created_date: The date when the task was created in iso format YYYY-MM-DDTHH:MM:SS+0000.
        focus_time: The focus time of the task.
        deleted: The status of the task. 0: not deleted, 1: deleted.
        tags: The tags of the task as a list of strings.
        project_id: The ID of the project of the task. For example: 6f8a2b3c4d5e1f09a7b6c8d9e0f2
        timezone: The timezone of the task.
        due_date: The due date of the task in format YYYY-MM-DD.
        column_id: ID of the column. For example: 4f9e8d7c6b5a4f0e9d8c7b6a5f4
        parent_id: The ID of the parent task, if the task has no parent the field will be empty.
                   For example: 6f8a2b3c4d5e1f09a7b6c8d9e0f2
    """
    title: str
    ticktick_id: str = field(eq=str.lower)
    ticktick_etag: str = field(eq=str.lower)
    created_date: str
    status: int = 0
    focus_time: float = 0
    deleted: int = 0
    tags: Tuple[str, ...] = ()
    project_id: str = field(default="", eq=str.lower)
    timezone: str = field(default="", eq=str.lower)
    due_date: str = field(default="", eq=str.lower)
    column_id: str = field(default="", eq=str.lower)
    parent_id: str = field(default="", eq=str.lower)
