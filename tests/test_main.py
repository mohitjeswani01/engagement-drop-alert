"""Integration tests for play/main.py."""

from unittest.mock import patch
import pytest
from play.main import run_pipeline
from play.store import load_posts, save_posts


def test_run_pipeline_empty_file(tmp_path):
    empty_file = tmp_path / "empty.json"
    summary = run_pipeline(str(empty_file))
    assert summary["total_posts"] == 0
    assert summary["newly_checked"] == 0
    assert summary["alerts_sent"] == 0


def test_run_pipeline_orchestration(tmp_path):
    log_file = tmp_path / "sample.json"
    posts_data = [
        {"date": "2026-08-01", "platform": "x", "likes": 100, "comments": 10},
        {"date": "2026-08-02", "platform": "x", "likes": 100, "comments": 10},
        {"date": "2026-08-03", "platform": "x", "likes": 10, "comments": 0},  # Underperforming
    ]
    save_posts(posts_data, str(log_file))

    with patch("play.main.send_telegram_alert", return_value=True) as mock_alert:
        summary = run_pipeline(str(log_file))

        assert summary["total_posts"] == 3
        assert summary["newly_checked"] == 3
        assert summary["alerts_sent"] == 1
        assert mock_alert.call_count == 1

        # Verify posts in file are now marked as checked
        updated_posts = load_posts(str(log_file))
        assert all(p.get("checked") is True for p in updated_posts)

    # Re-run pipeline: should not re-check or re-notify already checked posts
    with patch("play.main.send_telegram_alert", return_value=True) as mock_alert_2:
        summary_2 = run_pipeline(str(log_file))

        assert summary_2["total_posts"] == 3
        assert summary_2["newly_checked"] == 0
        assert summary_2["alerts_sent"] == 0
        assert mock_alert_2.call_count == 0


def test_run_pipeline_force_recheck(tmp_path):
    log_file = tmp_path / "sample.json"
    posts_data = [
        {"date": "2026-08-01", "platform": "x", "likes": 100, "comments": 10, "checked": True},
        {"date": "2026-08-02", "platform": "x", "likes": 10, "comments": 0, "checked": True},
    ]
    save_posts(posts_data, str(log_file))

    with patch("play.main.send_telegram_alert", return_value=True) as mock_alert:
        summary = run_pipeline(str(log_file), force_recheck=True)

        assert summary["newly_checked"] == 2
        assert summary["alerts_sent"] == 1
        assert mock_alert.call_count == 1
