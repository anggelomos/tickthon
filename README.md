# tickthon
Yet another unofficial Ticktick API client, it is based on ticktick-py https://pypi.org/project/ticktick-py/

## Installation
```bash
pip install tickthon
```

## Usage

```python
from tickthon import TicktickClient, TicktickListIds

client = TicktickClient(username, 
                        password, 
                        TicktickListIds(
                            INBOX="inbox-list-id",
                            TODAY_BACKLOG="today-list-id",
                            WEEK_BACKLOG="week-list-id",
                            MONTH_BACKLOG="month-list-id",
                            WEIGHT_MEASUREMENTS="weight-measurements-list-id"
                        )
            )
client.get_active_tasks()
```

## Features
- get_active_tasks()
- get_completed_tasks()
- get_deleted_tasks()
- get_abandoned_tasks()
- get_expense_logs()
- get_day_logs()
- get_task(task_id)
- get_overall_focus_time(date)
- get_active_focus_time(date, focus_tags_list)
- get_habits()
- complete_task(Task)
- create_task(Task, column_id)
- move_task_to_project(Task, project_id)

## Task model
This package uses a custom attrs model to store task data, it has the following attributes:

Task:
- title: str 
- status: int, default: 0  # 0: default/open, 2: done, -1: abandoned
- ticktick_id: str, default: ""
- focus_time: float, default: 0.0
- deleted: int, default: 0  # 0: not deleted, 1: deleted
- tags: List[str], default: []
- project_id: str, default: ""
- timezone: str, default: ""
- due_date: str, default: ""
- recurrent_id: Optional[str], default: ""

## Environment variables
- TT_USER: Ticktick username
- TT_PASS: Ticktick password
