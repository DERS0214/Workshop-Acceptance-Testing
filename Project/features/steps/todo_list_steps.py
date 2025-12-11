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


@when('the user adds a task "{title}"')
def step_when_add_task(context, title):
    context.added_task = context.todo.add_task(title)


@then('the to-do list should contain "{title}"')
def step_then_contains_task(context, title):
    titles = [task.title for task in context.todo.list_tasks()]
    assert title in titles, f"Expected '{title}' in {titles}"

