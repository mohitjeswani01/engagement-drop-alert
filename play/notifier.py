"""Notifier module for Engagement Drop Alert.

Sends notifications via Telegram when a post is flagged as underperforming.
Handles missing credentials and network errors gracefully.
"""

import json
import logging
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def format_alert_message(result: Dict[str, Any]) -> str:
    """Format an engagement drop result into a readable notification message."""
    date = result.get("date", "Unknown date")
    platform = str(result.get("platform", "Unknown platform")).capitalize()
    post_type = str(result.get("post_type", "Post")).capitalize()
    score = float(result.get("engagement_score", 0.0))
    rolling_avg = float(result.get("rolling_average", 0.0))
    percent_diff = float(result.get("percent_diff", 0.0))
    likes = result.get("likes", 0)
    comments = result.get("comments", 0)
    views = result.get("views")

    views_str = f"{views:,}" if views is not None else "N/A"

    msg = (
        f"⚠️ ENGAGEMENT DROP ALERT\n\n"
        f"📅 Date: {date}\n"
        f"📱 Platform: {platform} ({post_type})\n"
        f"📊 Performance Metrics:\n"
        f"   • Likes: {likes} | Comments: {comments} | Views: {views_str}\n"
        f"   • Current Score: {score:.2f}\n"
        f"   • Trailing Avg: {rolling_avg:.2f}\n"
        f"   • Underperforming by: {percent_diff:.1f}%\n\n"
        f"🚀 Action Recommended: Boost or reshare this post while it's still fresh!"
    )
    return msg


def send_telegram_alert(
    result: Dict[str, Any],
    token: Optional[str] = None,
    chat_id: Optional[str] = None,
    timeout: float = 10.0,
) -> bool:
    """Send a Telegram notification alert for an underperforming post.

    Args:
        result: Post analysis result dictionary.
        token: Telegram Bot Token (defaults to TELEGRAM_BOT_TOKEN env var).
        chat_id: Telegram Chat ID (defaults to TELEGRAM_CHAT_ID env var).
        timeout: Request timeout in seconds.

    Returns:
        True if sent successfully, False if missing config or failed.
    """
    bot_token = token or os.getenv("TELEGRAM_BOT_TOKEN")
    target_chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not target_chat_id:
        logger.warning(
            "Telegram alert skipped: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not configured."
        )
        return False

    message_text = format_alert_message(result)
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": target_chat_id,
        "text": message_text,
    }

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            res_body = response.read().decode("utf-8")
            res_json = json.loads(res_body)
            if res_json.get("ok"):
                return True
            logger.warning(f"Telegram API error response: {res_body}")
            return False
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        logger.warning(f"Failed to send Telegram notification: {exc}")
        return False
