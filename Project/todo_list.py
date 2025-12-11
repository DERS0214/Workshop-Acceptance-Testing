from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional


@dataclass
class Task:
    """Simple task model with basic metadata."""

    id: int
    title: str
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    def mark_completed(self) -> None:
        self.status = "completed"
        self.completed_at = datetime.utcnow()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }

    @staticmethod
    def from_dict(data: dict) -> "Task":
        return Task(
            id=int(data["id"]),
            title=data["title"],
            status=data.get("status", "pending"),
            created_at=datetime.fromisoformat(data["created_at"]),
            completed_at=datetime.fromisoformat(data["completed_at"])
            if data.get("completed_at")
            else None,
        )


class TodoList:
    """In-memory to-do list with optional JSON persistence."""

    def __init__(self, storage_path: Optional[Path] = None) -> None:
        self.storage_path = Path(storage_path) if storage_path else None
        self._tasks: List[Task] = []
        self._next_id = 1
        if self.storage_path:
            self._load()

    def _load(self) -> None:
        if not self.storage_path or not self.storage_path.exists():
            return
        raw = json.loads(self.storage_path.read_text(encoding="utf-8"))
        tasks = [Task.from_dict(item) for item in raw]
        self._tasks = tasks
        self._next_id = (max((t.id for t in tasks), default=0) or 0) + 1

    def _save(self) -> None:
        if not self.storage_path:
            return
        payload = [task.to_dict() for task in self._tasks]
        self.storage_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def add_task(self, title: str) -> Task:
        if not title.strip():
            raise ValueError("Task title cannot be empty")
        task = Task(id=self._next_id, title=title.strip())
        self._next_id += 1
        self._tasks.append(task)
        self._save()
        return task

    def list_tasks(self) -> List[Task]:
        return list(self._tasks)

    def mark_completed(self, task_id: int) -> Task:
        task = self._find_task_by_id(task_id)
        task.mark_completed()
        self._save()
        return task

    def clear(self) -> None:
        self._tasks.clear()
        self._save()

    def update_task(self, task_id: int, title: str) -> Task:
        if not title.strip():
            raise ValueError("Task title cannot be empty")
        task = self._find_task_by_id(task_id)
        task.title = title.strip()
        self._save()
        return task

    def _find_task_by_id(self, task_id: int) -> Task:
        for task in self._tasks:
            if task.id == task_id:
                return task
        raise ValueError(f"Task with id {task_id} not found")

    def __len__(self) -> int:
        return len(self._tasks)

    def __iter__(self) -> Iterable[Task]:
        return iter(self._tasks)


def _format_task(task: Task) -> str:
    marker = "x" if task.status == "completed" else " "
    return f"[{marker}] {task.id}: {task.title}"


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="To-Do List Manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("title", help="Title of the task")

    subparsers.add_parser("list", help="List all tasks")

    complete_parser = subparsers.add_parser(
        "complete", help="Mark a task as completed"
    )
    complete_parser.add_argument("id", type=int, help="ID of the task to complete")

    update_parser = subparsers.add_parser("update", help="Update a task title")
    update_parser.add_argument("id", type=int, help="ID of the task to update")
    update_parser.add_argument("title", help="New title for the task")

    subparsers.add_parser("clear", help="Clear all tasks")

    args = parser.parse_args(argv)
    todo = TodoList(storage_path=Path("todo_data.json"))

    if args.command == "add":
        task = todo.add_task(args.title)
        print(f"Added task {task.id}: {task.title}")
    elif args.command == "list":
        tasks = todo.list_tasks()
        if not tasks:
            print("No tasks found.")
        else:
            print("Tasks:")
            for task in tasks:
                print(f"- {_format_task(task)}")
    elif args.command == "complete":
        try:
            task = todo.mark_completed(args.id)
            print(f"Completed task {task.id}: {task.title}")
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 1
    elif args.command == "update":
        try:
            task = todo.update_task(args.id, args.title)
            print(f"Updated task {task.id}: {task.title}")
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 1
    elif args.command == "clear":
        todo.clear()
        print("Cleared all tasks.")
    else:
        parser.print_help()
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

