from typing import Optional, List

from attrs import define, field


@define
class Task:
    title: str = field(eq=False)
    status: int = field(default=0, eq=False)  # 0: default/open, 2: done, -1: abandoned
    ticktick_id: str = field(default="", eq=str.lower)
    focus_time: float = field(default=0, eq=False)
    deleted: int = field(default=0, eq=False)  # 0: not deleted, 1: deleted
    tags: List[str] = field(default=[], eq=False)
    project_id: str = field(default="", eq=False)
    timezone: str = field(default="", eq=str.lower)
    due_date: str = field(default="", eq=str.lower)
    kanban_status: str = field(default="", eq=False)
    recurrent_id: Optional[str] = field(default="", eq=False)
