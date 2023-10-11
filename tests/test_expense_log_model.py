import pytest

from tickthon import Task, ExpenseLog
from tickthon._task_utils import _parse_expense_log


@pytest.mark.parametrize("expense_title, expected_amount", [
    # Test with an integer expense amount.
    ("$99 Test expense log", 99),

    # Test with an integer expense amount.
    ("$99.9 Test expense log", 99.9),
])
def test_parse_expense_log(expense_title, expected_amount):
    expected_expense_log = ExpenseLog(date="9999-09-09", expense=expected_amount, product="Test expense log")
    raw_expense_log = Task(title=expense_title, due_date="9999-09-09",
                           ticktick_id="test", ticktick_etag="test")

    expense_log = _parse_expense_log(raw_expense_log)

    assert expense_log == expected_expense_log


@pytest.mark.parametrize("expense_title", [
    # Test with empty expense.
    "$",

    # Test with empty expense amount.
    "$ Test expense log",

    # Test with empty expense amount without spaces.
    "$Test expense log",
])
def test_parse_wrong_expense_log(expense_title):
    raw_expense_log = Task(title=expense_title, due_date="9999-09-09",
                           ticktick_id="test", ticktick_etag="test")

    expense_log = _parse_expense_log(raw_expense_log)

    assert expense_log is None
