from datetime import datetime

import pytest

from tickthon import Task
from tickthon import TicktickClient


@pytest.fixture(scope="module")
def ticktick_client(ticktick_info):
    return TicktickClient(ticktick_info["username"], ticktick_info["password"], ticktick_info["ticktick_ids"])


def test_get_active_tasks(ticktick_client):
    active_tasks = ticktick_client.get_active_tasks()

    assert len(active_tasks) > 0
    assert len(ticktick_client.all_active_tasks) >= len(active_tasks)


def test_get_deleted_tasks(ticktick_client):
    deleted_tasks = ticktick_client.get_deleted_tasks()
    assert len(deleted_tasks) > 0


def test_get_abandoned_tasks(ticktick_client):
    abandoned_tasks = ticktick_client.get_abandoned_tasks()
    assert len(abandoned_tasks) > 0


def test_get_completed_tasks(ticktick_client):
    completed_tasks = ticktick_client.get_completed_tasks()
    assert len(completed_tasks) > 0


def test_complete_task(ticktick_client):
    task_id = ticktick_client.create_task(Task(title="test-task", created_date="2099-09-09",
                                               ticktick_id="test-id", ticktick_etag="test-etag"))

    task_to_complete = ticktick_client.get_task(task_id)

    ticktick_client.complete_task(task_to_complete)

    completed_task = ticktick_client.get_task(task_to_complete.ticktick_id)
    assert completed_task.status == 2


def test_move_task(ticktick_client):
    inbox_project_id = ticktick_client.ticktick_list_ids.INBOX
    weight_measurements_id = ticktick_client.ticktick_list_ids.WEIGHT_MEASUREMENTS
    
    id_move_task = ticktick_client.create_task(Task(title="Test move task",
                                                    created_date="2099-09-09",
                                                    ticktick_id="test-move-id",
                                                    ticktick_etag="test-move-etag",
                                                    project_id=inbox_project_id))

    move_task = ticktick_client.get_task(id_move_task)
    ticktick_client.move_task_to_project(move_task, weight_measurements_id)

    moved_task = ticktick_client.get_task(id_move_task)
    assert moved_task.project_id == weight_measurements_id

    ticktick_client.complete_task(moved_task)


@pytest.mark.parametrize("task_tags", [tuple(), ("test-existing-tag",)])
def test_replace_task_tags(ticktick_client, task_tags):
    inbox_project_id = ticktick_client.ticktick_list_ids.INBOX
    id_task = ticktick_client.create_task(Task(title="Test replace task tags", created_date="2099-09-09",
                                               ticktick_id="test-tags-id", ticktick_etag="test-tags-etag",
                                               project_id=inbox_project_id, tags=task_tags))

    replace_tags_task = ticktick_client.get_task(id_task)

    ticktick_client.replace_task_tags(replace_tags_task, ("test-tickthon-tag",))
    active_tasks = ticktick_client.get_active_tasks()

    assert [task for task in active_tasks if task.ticktick_id == id_task][0].tags == ("test-tickthon-tag",)

    ticktick_client.complete_task(ticktick_client.get_task(id_task))


def test_get_overall_focus_time(ticktick_client):
    date = datetime.now().strftime("%Y-%m-%d")
    focus_time = ticktick_client.get_overall_focus_time(date)

    assert isinstance(focus_time, float)
    assert focus_time >= 0


def test_get_tasks_by_list(ticktick_client):
    test_list_id = ["687294a88f083d563d177ee6"]
    task_names = ["Test task - c13-bdb6", "Test task - e01f9b37-f6c0", "Test task - cb10f316ee1"]
    original_inbox_id = ticktick_client.ticktick_list_ids.INBOX
    ticktick_client.ticktick_list_ids.INBOX = test_list_id[0]
    ticktick_client._cached_raw_active_tasks = []

    tasks = ticktick_client.get_tasks_by_list(test_list_id)

    ticktick_client.ticktick_list_ids.INBOX = original_inbox_id
    assert len(tasks) == len(task_names)
    assert all(task.title in task_names for task in tasks)
