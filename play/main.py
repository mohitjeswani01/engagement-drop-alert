"""Main CLI orchestration module for Engagement Drop Alert.

Loads post log, analyzes performance, sends Telegram alerts for newly checked underperforming posts,
and persists updated 'checked' flags atomically.
"""

import argparse
import os
import sys
from typing import Any, Dict, List, Optional

from play.analyzer import analyze_posts
from play.notifier import send_telegram_alert
from play.store import get_default_log_path, load_posts, save_posts, StorageError


def print_summary_table(results: List[Dict[str, Any]], newly_checked_count: int, alerts_sent_count: int) -> None:
    """Print formatted terminal output summarizing the engagement analysis."""
    print("=" * 80)
    print(" 📊 ENGAGEMENT DROP ALERT — SUMMARY REPORT")
    print("=" * 80)
    print(f" Total Posts in Log: {len(results)}")
    print(f" Newly Checked Posts: {newly_checked_count}")
    print(f" Alerts Dispatched: {alerts_sent_count}")
    print("-" * 80)

    if not results:
        print(" No posts found in log.")
        print("=" * 80)
        return

    header = f"{'Date':<12} | {'Platform':<10} | {'Type':<8} | {'Score':<8} | {'Avg':<8} | {'Diff %':<8} | {'Status':<15}"
    print(header)
    print("-" * 80)

    for r in results:
        date = r.get("date", "")[:10]
        platform = str(r.get("platform", ""))[:10]
        post_type = str(r.get("post_type", ""))[:8]
        score = f"{r.get('engagement_score', 0.0):.1f}"
        rolling_avg = f"{r.get('rolling_average', 0.0):.1f}"
        diff = f"{r.get('percent_diff', 0.0):+.1f}%"

        if r.get("is_underperforming"):
            status = "⚠️ DROP ALERT"
        else:
            status = "✅ Normal"

        if not r.get("checked"):
            status += " (New)"

        print(f"{date:<12} | {platform:<10} | {post_type:<8} | {score:<8} | {rolling_avg:<8} | {diff:<8} | {status:<15}")

    print("=" * 80)


def run_pipeline(filepath: Optional[str] = None, force_recheck: bool = False) -> Dict[str, Any]:
    """Execute the full engagement drop alert pipeline.

    1. Loads post log.
    2. Computes rolling average and flags underperforming posts.
    3. Notifies via Telegram for newly checked underperforming posts.
    4. Marks processed posts as checked and saves log atomically.

    Args:
        filepath: Custom path to posts JSON file.
        force_recheck: If True, re-checks all posts even if previously checked.

    Returns:
        Summary dict containing counts and results.
    """
    log_path = filepath or get_default_log_path()

    try:
        raw_posts = load_posts(log_path)
    except StorageError as exc:
        print(f"❌ Storage Error: {exc}", file=sys.stderr)
        return {"error": str(exc), "total_posts": 0, "newly_checked": 0, "alerts_sent": 0}

    if not raw_posts:
        print(f"ℹ️  Post log at '{log_path}' is empty or does not exist.")
        return {"total_posts": 0, "newly_checked": 0, "alerts_sent": 0, "results": []}

    # Run analyzer
    results = analyze_posts(raw_posts)

    newly_checked_count = 0
    alerts_sent_count = 0

    # Process unchecked posts
    for idx, (raw_post, res) in enumerate(zip(raw_posts, results)):
        is_already_checked = raw_post.get("checked", False)

        if not is_already_checked or force_recheck:
            newly_checked_count += 1
            if res.get("is_underperforming"):
                sent = send_telegram_alert(res)
                if sent:
                    alerts_sent_count += 1

            # Mark post as checked
            raw_post["checked"] = True
            res["checked"] = True

    # Persist updated checked flags
    if newly_checked_count > 0:
        try:
            save_posts(raw_posts, log_path)
        except StorageError as exc:
            print(f"❌ Failed to persist updated check status: {exc}", file=sys.stderr)

    print_summary_table(results, newly_checked_count, alerts_sent_count)

    return {
        "total_posts": len(raw_posts),
        "newly_checked": newly_checked_count,
        "alerts_sent": alerts_sent_count,
        "results": results,
    }


def main() -> None:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description="Engagement Drop Alert CLI")
    parser.add_argument(
        "--file",
        "-f",
        type=str,
        default=None,
        help="Path to post log JSON file (defaults to POSTS_LOG_PATH env var or examples/sample_posts.json)",
    )
    parser.add_argument(
        "--force-recheck",
        action="store_true",
        help="Force re-checking all posts even if previously marked checked",
    )
    args = parser.parse_args()

    run_pipeline(filepath=args.file, force_recheck=args.force_recheck)


if __name__ == "__main__":
    main()
