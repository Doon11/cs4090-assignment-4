import pytest
import tempfile
import os
from tasks import (
    load_tasks, save_tasks, generate_unique_id,
    filter_tasks_by_priority, filter_tasks_by_category,
    filter_tasks_by_completion, search_tasks, get_overdue_tasks
)
from datetime import datetime, timedelta

@pytest.fixture
def sample_tasks():
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    return [
        {"id": 1, "title": "Task A", "description": "Alpha", "priority": "High", "category": "Work", "due_date": today, "completed": False},
        {"id": 2, "title": "Task B", "description": "Bravo", "priority": "Low", "category": "Personal", "due_date": yesterday, "completed": False},
        {"id": 3, "title": "Task C", "description": "Charlie", "priority": "Medium", "category": "School", "due_date": today, "completed": True},
    ]

def test_generate_unique_id(sample_tasks):
    assert generate_unique_id(sample_tasks) == 4

def test_filter_tasks_by_priority(sample_tasks):
    filtered = filter_tasks_by_priority(sample_tasks, "High")
    assert len(filtered) == 1 and filtered[0]["title"] == "Task A"

def test_filter_tasks_by_category(sample_tasks):
    filtered = filter_tasks_by_category(sample_tasks, "School")
    assert len(filtered) == 1 and filtered[0]["title"] == "Task C"

def test_filter_tasks_by_completion(sample_tasks):
    completed = filter_tasks_by_completion(sample_tasks, completed=True)
    assert len(completed) == 1 and completed[0]["title"] == "Task C"
    not_completed = filter_tasks_by_completion(sample_tasks, completed=False)
    assert len(not_completed) == 2

def test_search_tasks(sample_tasks):
    results = search_tasks(sample_tasks, "Bravo")
    assert len(results) == 1 and results[0]["title"] == "Task B"

def test_get_overdue_tasks(sample_tasks):
    overdue = get_overdue_tasks(sample_tasks)
    assert len(overdue) == 1 and overdue[0]["title"] == "Task B"

def test_save_and_load_tasks(sample_tasks):
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        save_tasks(sample_tasks, tmp.name)
        loaded = load_tasks(tmp.name)
        assert loaded == sample_tasks
    os.unlink(tmp.name)