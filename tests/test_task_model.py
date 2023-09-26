import attrs
from tickthon import Task, dict_to_task
from tickthon._task_utils import _get_focus_time, _get_task_date, _get_kanban_status


def test_dict_to_task(dict_task):
    expected_task = Task(ticktick_id="60c8d7b1e9b80e0595353bc6",
                         status=0,
                         title="Automation tasks",
                         focus_time=0.1,
                         deleted=0,
                         tags=["test", "unit"],
                         project_id="5f30772022d478db3ad1a9c2",
                         timezone="America/Bogota",
                         due_date="2023-08-03",
                         kanban_status="",
                         recurrent_id="o3k8772022d478db3ad1d94j"
                         )

    task = dict_to_task(dict_task)

    assert attrs.asdict(task) == attrs.asdict(expected_task)


def test_get_ticktick_focus_time():
    rawt_focus_time = {"focusSummaries": [{"pomoDuration": 0, "stopwatchDuration": 100},
                                          {"pomoDuration": 260, "stopwatchDuration": 0},
                                          ]}

    focus_time = _get_focus_time(rawt_focus_time)

    assert focus_time == 0.1


def test_get_focus_time():
    raw_focus_time = {"focus_time": 0.1}

    focus_time = _get_focus_time(raw_focus_time)

    assert focus_time == 0.1


def test_get_date():
    raw_task_date = "2023-08-03T19:15:00.000+0000"
    raw_timezone = "America/Bogota"

    task_date = _get_task_date(raw_timezone, raw_task_date)

    assert task_date == "2023-08-03"


def test_get_kanban_status():
    column_id = "61c62f48824afc6c76352411"
    kanban_status = _get_kanban_status(column_id)

    assert kanban_status == "review"


def test_get_empty_kanban_status():
    column_id = _get_kanban_status("")
    assert column_id == ""
