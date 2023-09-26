from datetime import datetime
from typing import Optional

from ..task_model import Task


class TicktickPayloads:

    @staticmethod
    def get_habits_checkins(habit_list: dict, after_stamp: int) -> dict:
        return {
            "habitIds": list(habit_list.keys()),
            "afterStamp": after_stamp
        }

    @classmethod
    def complete_task(cls, task_id: str, project_id: str) -> dict:
        return {
            "update": [
                {
                    "completedUserId": 114478622,
                    "status": 2,
                    "projectId": project_id,
                    "completedTime": f"{datetime.utcnow()}+0000",
                    "id": task_id
                }
            ]
        }

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
