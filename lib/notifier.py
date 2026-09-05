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


def generate_action_recommendation(result: Dict[str, Any]) -> str:
    """Generate a dynamic, platform and severity-aware recommendation."""
    platform = str(result.get("platform", "")).lower()
    post_type = str(result.get("post_type", "")).lower()
    percent_diff = float(result.get("percent_diff", 0.0))
    comments = int(result.get("comments") or 0)
    likes = int(result.get("likes") or 0)
    views = result.get("views")

    # Platform & post_type specific tactics
    if "instagram" in platform:
        if "reel" in post_type:
            platform_advice = "Share to Stories with an interactive poll or cross-post to Threads to reignite views."
        else:
            platform_advice = "Post a follow-up Story asking a question or reply to comments to boost algorithmic ranking."
    elif "x" in platform or "twitter" in platform:
        platform_advice = "Quote-tweet with a new provocative angle or post a follow-up reply thread to spark engagement."
    elif "youtube" in platform:
        platform_advice = "Tweak the title/thumbnail for a higher CTR, or pin an engaging question in the comments."
    elif "tiktok" in platform:
        platform_advice = "Reply to top comments with a video response or share to your Story with a sticker."
    elif "linkedin" in platform:
        platform_advice = "Tag key collaborators in a comment or add a detailed thought to jumpstart post visibility."
    else:
        platform_advice = "Reshare with an updated caption or cross-promote on your other active channels."

    # Severity prefix
    if percent_diff >= 70.0:
        severity = f"🔥 Severe drop ({percent_diff:.1f}% below avg)."
    else:
        severity = f"💡 Drop detected ({percent_diff:.1f}% below avg)."

    # Metric specific hint
    if comments < 5 and likes > 20:
        metric_hint = " Comments are lagging — ask your audience a direct question in the replies!"
    elif views is not None and int(views) < 1500:
        metric_hint = " Views are lagging — re-engage your audience with a direct link share."
    else:
        metric_hint = " Boost or reshare while the post is still fresh!"

    return f"{severity} {platform_advice} {metric_hint}"


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
    recommendation = generate_action_recommendation(result)

    msg = (
        f"⚠️ ENGAGEMENT DROP ALERT\n\n"
        f"📅 Date: {date}\n"
        f"📱 Platform: {platform} ({post_type})\n"
        f"📊 Performance Metrics:\n"
        f"   • Likes: {likes} | Comments: {comments} | Views: {views_str}\n"
        f"   • Current Score: {score:.2f}\n"
        f"   • Trailing Avg: {rolling_avg:.2f}\n"
        f"   • Underperforming by: {percent_diff:.1f}%\n\n"
        f"🚀 Action Recommended:\n{recommendation}"
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
