from datetime import datetime
from typing import Optional, Collection

from ..task_model import Task


class TicktickPayloads:

    @staticmethod
    def get_habits_checkins(habit_list: dict, after_stamp: int) -> dict:
        return {
            "habitIds": list(habit_list.keys()),
            "afterStamp": after_stamp
        }

    @staticmethod
    def _update_task(task_id: str, project_id: str, status: int | None = None, completed_time: str | None = None,
                     tags: Collection[str] | None = None) -> dict:
        payload = {
            "update": [
                {
                    "completedUserId": 114478622,
                    "projectId": project_id,
                    "id": task_id
                }
            ]
        }

        if status:
            payload["update"][0]["status"] = status

        if completed_time:
            payload["update"][0]["completedTime"] = completed_time

        if tags is not None:
            payload["update"][0]["tags"] = tags

        return payload

    @classmethod
    def complete_task(cls, task: Task) -> dict:
        return cls._update_task(task.ticktick_id, task.project_id, status=2, completed_time=f"{datetime.utcnow()}+0000")

    @classmethod
    def update_task_tags(cls, task: Task, tags: Collection[str]) -> dict:
        return cls._update_task(task.ticktick_id, task.project_id, tags=tags)

    @classmethod
    def move_task_to_project(cls, task: Task, project_id: str) -> list[dict]:
        return [
            {
                "fromProjectId": task.project_id,
                "toProjectId": project_id,
                "taskId": task.ticktick_id,
            }
        ]

    @classmethod
    def create_task(cls, task: Task, column_id: Optional[str] = None) -> dict:
        return {
            "add": [
                {
                    "startDate": task.due_date if task.due_date else None,
                    "columnId": column_id,
                    "projectId": task.project_id if task.project_id else None,
                    "title": task.title,
                    "tags": task.tags if task.tags else None,
                    "timeZone": task.timezone if task.timezone else None,
                }
            ],
            "update": [],
            "delete": [],
            "addAttachments": [],
            "updateAttachments": [],
            "deleteAttachments": []
        }
