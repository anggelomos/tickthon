# tickthon
Yet another unofficial Ticktick API client, it is based on ticktick-py https://pypi.org/project/ticktick-py/

## Installation
```bash
pip install tickthon
```

## Usage

```python
from tickthon import TicktickClient

client = TicktickClient(username, password)
client.get_active_tasks()
```

## Features
- get_active_tasks()
- get_completed_tasks()
- get_deleted_tasks()
- get_abandoned_tasks()
- get_task(task_id)
- get_habits()
- complete_task(Task)
- create_task(Task, column_id)


## Task model
This packages uses a custom attrs model to store task data, it has the following attributes:

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
- kanban_status: str, default: ""
- recurrent_id: Optional[str], default: ""

## Environment variables
- TT_USER: Ticktick username
- TT_PASS: Ticktick password
- TICKTICK_IDS: This variable should be a json string with the following keys:

for example:
```json
{
  "project_id": "project_name",
  "project_id2": "project_name2",
  "project_id3": "project_name3"
}
```
*Note*: Remember that it is an optional step, if you don't set this variable the package will still work.
