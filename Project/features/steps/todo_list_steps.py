import os
import sys

from behave import given, then, when

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from todo_list import TodoList  # noqa: E402


@given("the to-do list is empty")
def step_given_empty_list(context):
    context.todo = TodoList(storage_path=None)


@given("the to-do list contains tasks:")
def step_given_list_with_tasks(context):
    context.todo = TodoList(storage_path=None)
    for row in context.table:
        title = row.get("Task") or row[0]
        status = (row.get("Status") or "Pending").lower()
        task = context.todo.add_task(title)
        if status == "completed":
            context.todo.mark_completed(task.id)


@when('the user adds a task "{title}"')
def step_when_add_task(context, title):
    context.added_task = context.todo.add_task(title)


@when("the user lists all tasks")
def step_when_list_tasks(context):
    tasks = context.todo.list_tasks()
    lines = ["Tasks:"]
    for task in tasks:
        lines.append(f"- {task.title}")
    context.list_output = "\n".join(lines)


@then('the to-do list should contain "{title}"')
def step_then_contains_task(context, title):
    titles = [task.title for task in context.todo.list_tasks()]
    assert title in titles, f"Expected '{title}' in {titles}"


@then("the output should contain:")
def step_then_output_contains(context):
    expected_lines = [line.strip() for line in context.text.strip().splitlines()]
    actual_lines = [line.strip() for line in context.list_output.strip().splitlines()]
    for expected in expected_lines:
        assert expected in actual_lines, f"Expected line '{expected}' not found in output"

