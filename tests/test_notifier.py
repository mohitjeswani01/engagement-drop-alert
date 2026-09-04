"""Unit tests for play/notifier.py."""

import json
from unittest.mock import MagicMock, patch
import urllib.error
import pytest
from play.notifier import format_alert_message, send_telegram_alert


def test_format_alert_message():
    result = {
        "date": "2026-08-20",
        "platform": "instagram",
        "post_type": "reel",
        "likes": 100,
        "comments": 10,
        "views": 5000,
        "engagement_score": 180.0,
        "rolling_average": 300.0,
        "percent_diff": 40.0,
    }
    msg = format_alert_message(result)
    assert "⚠️ ENGAGEMENT DROP ALERT" in msg
    assert "2026-08-20" in msg
    assert "Instagram (Reel)" in msg
    assert "Underperforming by: 40.0%" in msg
    assert "Boost or reshare" in msg


def test_send_telegram_alert_missing_credentials(monkeypatch):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)

    result = {"date": "2026-08-20", "platform": "x"}
    assert send_telegram_alert(result) is False


def test_send_telegram_alert_success(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "mock_token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "mock_chat_id")

    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({"ok": True}).encode("utf-8")
    mock_response.__enter__.return_value = mock_response

    with patch("urllib.request.urlopen", return_value=mock_response) as mock_urlopen:
        result = {"date": "2026-08-20", "platform": "x", "engagement_score": 10.0}
        success = send_telegram_alert(result)
        assert success is True
        assert mock_urlopen.called


def test_send_telegram_alert_api_failure(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "mock_token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "mock_chat_id")

    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({"ok": False, "description": "Forbidden"}).encode("utf-8")
    mock_response.__enter__.return_value = mock_response

    with patch("urllib.request.urlopen", return_value=mock_response):
        result = {"date": "2026-08-20", "platform": "x"}
        success = send_telegram_alert(result)
        assert success is False


def test_send_telegram_alert_network_error(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "mock_token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "mock_chat_id")

    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("Network unreachable")):
        result = {"date": "2026-08-20", "platform": "x"}
        success = send_telegram_alert(result)
        assert success is False
