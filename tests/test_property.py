import pytest
import tempfile
import os
from tasks import (
    load_tasks, save_tasks, generate_unique_id,
    filter_tasks_by_priority, filter_tasks_by_category
)
from datetime import datetime
from hypothesis import given, strategies

# Strategy to generate mock tasks
@strategies.composite
def task_strategy(draw):
    return {
        "id": draw(strategies.integers(min_value=1, max_value=10000)),
        "title": draw(strategies.text(min_size=1, max_size=100)),
        "description": draw(strategies.text(min_size=0, max_size=200)),
        "priority": draw(strategies.sampled_from(["Low", "Medium", "High"])),
        "category": draw(strategies.sampled_from(["Work", "Personal", "School", "Other"])),
        "due_date": draw(strategies.dates(min_value=datetime(2000, 1, 1).date(), max_value=datetime(2100, 1, 1).date())).strftime("%Y-%m-%d"),
        "completed": draw(strategies.booleans()),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


@given(strategies.lists(task_strategy(), min_size=0, max_size=100))
def test_generate_unique_id_is_unique(task_list):
    existing_ids = {task["id"] for task in task_list}
    new_id = generate_unique_id(task_list)
    assert new_id not in existing_ids
    assert isinstance(new_id, int)


@given(strategies.lists(task_strategy(), min_size=1), strategies.sampled_from(["Low", "Medium", "High"]))
def test_filter_tasks_by_priority_returns_correct_priority(tasks, priority):
    filtered = filter_tasks_by_priority(tasks, priority)
    for task in filtered:
        assert task["priority"] == priority


@given(strategies.lists(task_strategy(), min_size=1), strategies.sampled_from(["Work", "Personal", "School", "Other"]))
def test_filter_tasks_by_category_returns_correct_category(tasks, category):
    filtered = filter_tasks_by_category(tasks, category)
    for task in filtered:
        assert task["category"] == category


@given(strategies.lists(task_strategy(), min_size=1, max_size=50))
def test_save_and_load_is_consistent(task_list):
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        save_tasks(task_list, tmp.name)
        loaded = load_tasks(tmp.name)
        assert loaded == task_list
    os.unlink(tmp.name)
