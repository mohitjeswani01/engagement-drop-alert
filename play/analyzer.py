"""Engagement analyzer module.

Calculates engagement scores and trailing rolling averages for social media posts,
flagging posts that fall significantly below historical performance.
"""

import os
from typing import Any, Dict, List, Optional


def calculate_engagement_score(post: Dict[str, Any]) -> float:
    """Calculate engagement score for a single post.

    Formula: likes + (comments * 3.0) + (views * 0.01)
    - Comments are weighted 3x because they signal higher intent.
    - Views are weighted 0.01x because view counts are orders of magnitude higher.
    - Missing, None, or invalid numeric fields default to 0.0.

    Args:
        post: Dictionary containing post fields (likes, comments, views).

    Returns:
        Float engagement score rounded to 2 decimal places.
    """
    def _parse_num(val: Any) -> float:
        if val is None:
            return 0.0
        try:
            parsed = float(val)
            return max(0.0, parsed)
        except (ValueError, TypeError):
            return 0.0

    likes = _parse_num(post.get("likes"))
    comments = _parse_num(post.get("comments"))
    views = _parse_num(post.get("views"))

    score = likes + (comments * 3.0) + (views * 0.01)
    return round(score, 2)


def analyze_posts(
    posts: List[Dict[str, Any]],
    window_size: Optional[int] = None,
    threshold_percent: Optional[float] = None,
) -> List[Dict[str, Any]]:
    """Analyze a list of post entries in chronological order.

    Computes a trailing rolling average of engagement scores over the previous N posts
    (excluding the post currently being evaluated). Flags any post whose engagement score
    drops more than threshold_percent below its trailing rolling average.

    Args:
        posts: List of post dictionaries.
        window_size: Trailing window size N (defaults to ROLLING_WINDOW_SIZE env var or 5).
        threshold_percent: Drop threshold % (defaults to UNDERPERFORM_THRESHOLD_PERCENT env var or 40.0).

    Returns:
        List of structured result dictionaries for each post.
    """
    if window_size is None:
        try:
            window_size = int(os.getenv("ROLLING_WINDOW_SIZE", "5"))
        except ValueError:
            window_size = 5

    if threshold_percent is None:
        try:
            threshold_percent = float(os.getenv("UNDERPERFORM_THRESHOLD_PERCENT", "40.0"))
        except ValueError:
            threshold_percent = 40.0

    if window_size <= 0:
        window_size = 5
    if threshold_percent < 0:
        threshold_percent = 40.0

    results: List[Dict[str, Any]] = []
    if not posts:
        return results

    # Process each post in order
    for i, post in enumerate(posts):
        score = calculate_engagement_score(post)

        # Baseline window uses up to window_size previous posts [i - N, i - 1]
        start_idx = max(0, i - window_size)
        history_posts = posts[start_idx:i]
        sample_size = len(history_posts)

        if sample_size > 0:
            history_scores = [calculate_engagement_score(p) for p in history_posts]
            rolling_avg = sum(history_scores) / sample_size
            rolling_avg = round(rolling_avg, 2)
        else:
            # First post has no history baseline
            rolling_avg = score
            sample_size = 0

        # Calculate percentage difference relative to rolling average
        if sample_size > 0 and rolling_avg > 0:
            percent_diff = ((rolling_avg - score) / rolling_avg) * 100.0
            percent_diff = round(percent_diff, 2)
        else:
            percent_diff = 0.0

        is_underperforming = bool(sample_size > 0 and percent_diff >= threshold_percent)

        def _safe_int_or_none(val: Any) -> Optional[int]:
            if val is None:
                return None
            try:
                return int(val)
            except (ValueError, TypeError):
                return None

        result = {
            "date": str(post.get("date", "")),
            "platform": str(post.get("platform", "unknown")),
            "post_type": str(post.get("post_type", "post")),
            "likes": _safe_int_or_none(post.get("likes")) or 0,
            "comments": _safe_int_or_none(post.get("comments")) or 0,
            "views": _safe_int_or_none(post.get("views")),
            "engagement_score": score,
            "rolling_average": rolling_avg,
            "percent_diff": percent_diff,
            "is_underperforming": is_underperforming,
            "sample_size": sample_size,
            "checked": bool(post.get("checked", False)),
        }
        results.append(result)

    return results
