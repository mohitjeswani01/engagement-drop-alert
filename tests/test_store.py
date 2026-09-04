"""Unit tests for play/store.py."""

import json
import os
import pytest
from play.store import load_posts, save_posts, StorageError


def test_load_posts_non_existent_file(tmp_path):
    log_file = tmp_path / "non_existent.json"
    posts = load_posts(str(log_file))
    assert posts == []


def test_load_posts_empty_file(tmp_path):
    log_file = tmp_path / "empty.json"
    log_file.write_text("")
    posts = load_posts(str(log_file))
    assert posts == []


def test_save_and_load_posts(tmp_path):
    log_file = tmp_path / "posts.json"
    sample_data = [
        {"date": "2026-08-20", "platform": "instagram", "likes": 100, "comments": 5}
    ]
    save_posts(sample_data, str(log_file))

    loaded = load_posts(str(log_file))
    assert loaded == sample_data


def test_load_posts_corrupted_json(tmp_path):
    log_file = tmp_path / "corrupt.json"
    log_file.write_text("{this is not valid json")

    with pytest.raises(StorageError) as exc_info:
        load_posts(str(log_file))

    assert "Corrupted JSON log" in str(exc_info.value)

    # Verify backup file was created
    corrupt_files = list(tmp_path.glob("corrupt.json.corrupt.*"))
    assert len(corrupt_files) == 1
    assert corrupt_files[0].read_text() == "{this is not valid json"


def test_load_posts_not_a_list(tmp_path):
    log_file = tmp_path / "dict.json"
    log_file.write_text('{"key": "value"}')

    with pytest.raises(StorageError) as exc_info:
        load_posts(str(log_file))

    assert "Expected JSON array" in str(exc_info.value)


def test_save_posts_creates_parent_dirs(tmp_path):
    nested_file = tmp_path / "sub" / "dir" / "posts.json"
    sample_data = [{"date": "2026-08-21", "likes": 50}]
    save_posts(sample_data, str(nested_file))

    assert os.path.exists(str(nested_file))
    assert load_posts(str(nested_file)) == sample_data


def test_default_env_var_path(tmp_path, monkeypatch):
    env_file = tmp_path / "env_posts.json"
    monkeypatch.setenv("POSTS_LOG_PATH", str(env_file))

    sample_data = [{"date": "2026-08-22", "likes": 75}]
    save_posts(sample_data)
    loaded = load_posts()
    assert loaded == sample_data
