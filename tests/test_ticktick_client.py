import json
from typing import List

import pytest

from tickthon import Task, ExpenseLog
from tickthon import TicktickClient


@pytest.fixture(scope="module")
def ticktick_client(ticktick_info):
    return TicktickClient(ticktick_info["username"], ticktick_info["password"])


def test_get_project_list(ticktick_client, data_folder_path):
    expected_project_lists = {"90as8dfa09sd8f90asdf809": "test-project",
                              "90as8dfa0as23dfsdf809": "test-project",
                              "90as8df23f2390asdf809": "test-project",
                              "90as823fw3sd8f90asdf809": "test-project",
                              "90as8dfa23432fdsasdf809": "test-project",
                              "90as8df324fds8f90asdf809": "test-project",
                              "90as8d234sdf9sd8f90asdf809": "test-project"}
    with open(data_folder_path / "project_profiles.json") as f:
        lists = json.load(f)

    project_lists = ticktick_client._get_project_lists(lists)

    assert project_lists == expected_project_lists


def test_get_active_tasks(ticktick_client):
    active_tasks = ticktick_client.get_active_tasks()

    assert len(active_tasks) > 0
    assert len(ticktick_client.all_active_tasks) >= len(active_tasks)


def test_get_completed_tasks(ticktick_client):
    completed_tasks = ticktick_client.get_completed_tasks()
    assert len(completed_tasks) > 0


def test_get_ideas(ticktick_client):
    id_idea = ticktick_client.create_task(Task(title="Idea: test idea",
                                               ticktick_id="test-id", ticktick_etag="test-etag"))

    ideas = ticktick_client.get_ideas()

    assert len(ideas) > 0
    assert isinstance(ideas, List) and all(isinstance(i, Task) for i in ideas)
    ticktick_client.complete_task(ticktick_client.get_task(id_idea))


def test_get_expense_logs(ticktick_client):
    id_expense_log = ticktick_client.create_task(Task(title="$100 test expense log",
                                                      ticktick_id="test-id", ticktick_etag="test-etag"))

    expense_logs = ticktick_client.get_expense_logs()

    assert len(expense_logs) > 0
    assert isinstance(expense_logs, List) and all(isinstance(i, ExpenseLog) for i in expense_logs)
    ticktick_client.complete_task(ticktick_client.get_task(id_expense_log))


def test_complete_task(ticktick_client):
    task_id = ticktick_client.create_task(Task(title="test-task",
                                               ticktick_id="test-id", ticktick_etag="test-etag"))

    task_to_complete = ticktick_client.get_task(task_id)

    ticktick_client.complete_task(task_to_complete)

    completed_task = ticktick_client.get_task(task_to_complete.ticktick_id)
    assert completed_task.status == 2


def test_get_habits(ticktick_client):
    habits = ticktick_client.get_habits()

    assert len(habits) >= 1
    assert isinstance(habits, dict)
    assert isinstance(list(habits.values())[0], list)
    assert isinstance(list(habits.values())[0][0], str)

# TODO: Create a test for get_deleted_tasks
# TODO: Create a test for get_abandoned_tasks
