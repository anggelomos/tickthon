from enum import Enum


class TicktickIdKeys(Enum):
    FOLDER_IDS = "FOLDER_IDS"
    LIST_IDS = "LIST_IDS"


class TicktickFolderKeys(Enum):
    INBOX_TASKS = "inbox_tasks"
    LIFE_KANBAN = "life_kanban"
    CURRENT_BACKLOG = "current_backlog"
    TASKS_BACKLOG = "tasks_backlog"
    LONG_TERM_REMINDERS = "long_term_reminders"
    WORK_TASKS = "work_tasks"
    WORK_REMINDERS = "work_reminders"
    WEIGHT_MEASUREMENTS = "weight_measurements"
    DAY_LOGS = "day_logs"
