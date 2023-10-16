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
- get_ideas()
- get_expense_logs()
- get_task(task_id)
- get_overall_focus_time(date)
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
- recurrent_id: Optional[str], default: ""

## Environment variables
- TT_USER: Ticktick username
- TT_PASS: Ticktick password
- TICKTICK_IDS: This environment variable is a JSON string that specifies the TickTick lists and folders from which 
  tasks will be fetched, if you don't set this environment variable all tasks will be fetched. It follows this structure:

for example:
```json
{
  "FOLDER_IDS": {
    "folder_name-1": "folder_id",
    "folder_name-2": "folder_id",
    ...
  },
  "LIST_IDS": {
    "list_name-1": "list_id",
    "list_name-2": "list_id",
    ...
  }
}
```
*Note*: Remember that it is an optional step, if you don't set this variable the package will still work.
