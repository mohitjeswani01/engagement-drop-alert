"""Storage module for engagement drop alert.

Handles loading and saving social media post logs with atomic writes
and corrupted file recovery.
"""

import json
import os
import shutil
import tempfile
from datetime import datetime
from typing import Any, Dict, List, Optional


class StorageError(Exception):
    """Exception raised for storage operation failures."""
    pass


def get_default_log_path() -> str:
    """Get default log file path from POSTS_LOG_PATH env var or fallback."""
    return os.getenv("POSTS_LOG_PATH", "examples/sample_posts.json")


def load_posts(filepath: Optional[str] = None) -> List[Dict[str, Any]]:
    """Load post performance entries from JSON file.

    If file does not exist, returns an empty list.
    If file is corrupt, creates a backup file (.corrupt.<timestamp>) and raises StorageError.

    Args:
        filepath: Path to posts log JSON file. Defaults to POSTS_LOG_PATH env var.

    Returns:
        List of post dictionaries.

    Raises:
        StorageError: If JSON structure is corrupt or unparseable.
    """
    path = filepath or get_default_log_path()

    if not os.path.exists(path):
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []
            data = json.loads(content)
            if not isinstance(data, list):
                raise StorageError(f"Expected JSON array in {path}, got {type(data).__name__}")
            return data
    except json.JSONDecodeError as exc:
        # Backup corrupted file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        corrupt_backup = f"{path}.corrupt.{timestamp}"
        try:
            shutil.copy2(path, corrupt_backup)
        except IOError:
            pass
        raise StorageError(
            f"Corrupted JSON log at '{path}': {exc}. Backed up to '{corrupt_backup}'."
        ) from exc
    except IOError as exc:
        raise StorageError(f"Failed to read post log at '{path}': {exc}") from exc


def save_posts(posts: List[Dict[str, Any]], filepath: Optional[str] = None) -> None:
    """Atomically save post performance entries to JSON file.

    Writes to a temporary file in the target directory and replaces the target file.

    Args:
        posts: List of post dictionaries to save.
        filepath: Path to target JSON file. Defaults to POSTS_LOG_PATH env var.

    Raises:
        StorageError: If atomic save operation fails.
    """
    path = filepath or get_default_log_path()
    dir_name = os.path.dirname(path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)

    temp_fd = None
    temp_path = None
    try:
        temp_fd, temp_path = tempfile.mkstemp(dir=dir_name or ".", prefix=".posts_log_", suffix=".tmp")
        with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
            json.dump(posts, f, indent=2, ensure_ascii=False)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())

        os.replace(temp_path, path)
    except Exception as exc:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
        raise StorageError(f"Failed to atomically save posts to '{path}': {exc}") from exc
