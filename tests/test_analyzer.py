"""Unit tests for play/analyzer.py."""

import pytest
from play.analyzer import calculate_engagement_score, analyze_posts


def test_calculate_engagement_score_basic():
    post = {"likes": 100, "comments": 10, "views": 1000}
    # 100 + (10 * 3.0) + (1000 * 0.01) = 100 + 30 + 10 = 140.0
    assert calculate_engagement_score(post) == 140.0


def test_calculate_engagement_score_missing_views():
    post = {"likes": 50, "comments": 5}
    # 50 + (5 * 3.0) + 0 = 65.0
    assert calculate_engagement_score(post) == 65.0


def test_calculate_engagement_score_none_and_invalid_values():
    post = {"likes": "invalid", "comments": None, "views": -500}
    # "invalid" -> 0, None -> 0, -500 -> max(0, -500) = 0
    assert calculate_engagement_score(post) == 0.0


def test_analyze_posts_empty_list():
    assert analyze_posts([]) == []


def test_analyze_posts_single_post():
    posts = [{"date": "2026-08-20", "platform": "x", "likes": 10, "comments": 2}]
    results = analyze_posts(posts)
    assert len(results) == 1
    assert results[0]["engagement_score"] == 16.0  # 10 + 6
    assert results[0]["rolling_average"] == 16.0
    assert results[0]["sample_size"] == 0
    assert results[0]["percent_diff"] == 0.0
    assert results[0]["is_underperforming"] is False


def test_analyze_posts_baseline_excludes_current_post():
    posts = [
        {"date": "2026-08-01", "likes": 100, "comments": 0, "views": 0},  # score 100
        {"date": "2026-08-02", "likes": 200, "comments": 0, "views": 0},  # score 200
    ]
    results = analyze_posts(posts, window_size=5, threshold_percent=40.0)

    # Post 0: no prior history
    assert results[0]["engagement_score"] == 100.0
    assert results[0]["rolling_average"] == 100.0
    assert results[0]["sample_size"] == 0

    # Post 1: baseline is Post 0 only (score 100.0)
    assert results[1]["engagement_score"] == 200.0
    assert results[1]["rolling_average"] == 100.0
    assert results[1]["sample_size"] == 1
    assert results[1]["percent_diff"] == -100.0  # 200 vs 100 baseline: 100% above baseline (-100% drop)
    assert results[1]["is_underperforming"] is False


def test_analyze_posts_underperforming_detection():
    # 5 baseline posts around 100 score, then post 6 drops to 30 score (70% drop)
    posts = [
        {"date": f"2026-08-0{i}", "likes": 100, "comments": 0, "views": 0} for i in range(1, 6)
    ]
    posts.append({"date": "2026-08-06", "likes": 30, "comments": 0, "views": 0})

    results = analyze_posts(posts, window_size=5, threshold_percent=40.0)

    last_post_result = results[-1]
    assert last_post_result["engagement_score"] == 30.0
    assert last_post_result["rolling_average"] == 100.0
    assert last_post_result["sample_size"] == 5
    assert last_post_result["percent_diff"] == 70.0  # (100 - 30)/100 * 100
    assert last_post_result["is_underperforming"] is True


def test_analyze_posts_window_size_limit():
    # 10 posts with scores 10 to 100. Window size=3.
    posts = [
        {"date": f"2026-08-{i:02d}", "likes": i * 10, "comments": 0, "views": 0}
        for i in range(1, 11)
    ]
    results = analyze_posts(posts, window_size=3)

    # For post index 5 (score 60): baseline uses indices 2, 3, 4 (scores 30, 40, 50) -> avg 40
    p5 = results[5]
    assert p5["engagement_score"] == 60.0
    assert p5["rolling_average"] == 40.0
    assert p5["sample_size"] == 3


def test_analyze_posts_custom_threshold(monkeypatch):
    monkeypatch.setenv("UNDERPERFORM_THRESHOLD_PERCENT", "20.0")
    posts = [
        {"date": "2026-08-01", "likes": 100, "comments": 0},
        {"date": "2026-08-02", "likes": 75, "comments": 0},  # 25% drop (underperforms 20% threshold)
    ]
    results = analyze_posts(posts)
    assert results[1]["percent_diff"] == 25.0
    assert results[1]["is_underperforming"] is True
