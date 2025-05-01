import pytest
import tempfile
import os
from tasks import (
    load_tasks, save_tasks, generate_unique_id,
    filter_tasks_by_priority, filter_tasks_by_category,
    filter_tasks_by_completion, search_tasks, get_overdue_tasks
)

def test_generate_unique_id_empty_list():
    assert generate_unique_id([]) == 1

def test_load_tasks_missing_file():
    assert not load_tasks("non-existant.json")
