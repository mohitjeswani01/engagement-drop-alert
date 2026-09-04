# 📉 Engagement Drop Alert — Zero-API Social Media Monitor

A platform-agnostic, zero-API social media performance monitor. Manually log your post performance across **Instagram**, **YouTube**, **X (Twitter)**, **TikTok**, **LinkedIn**, or any other channel, and automatically detect when a recent post is underperforming its trailing average so you can boost or reshare while it's still fresh.

---

## ⚡ Why Zero-API?

- **No Developer Accounts**: No OAuth tokens, no platform API approvals, no rate limits.
- **Platform-Agnostic**: Works for any platform (free-text platform and post_type labels).
- **Zero-Setup Privacy**: Runs 100% locally on your machine in under 2 minutes.

---

## 🚀 2-Minute Quickstart

### 1. Prerequisites
Python 3.10+ installed. Zero external runtime dependencies required!

### 2. Run with Sample Data
```bash
python3 -m play.main --file examples/sample_posts.json
```

Output:
```text
================================================================================
 📊 ENGAGEMENT DROP ALERT — SUMMARY REPORT
================================================================================
 Total Posts in Log: 6
 Newly Checked Posts: 6
 Alerts Dispatched: 0
--------------------------------------------------------------------------------
Date         | Platform   | Type     | Score    | Avg      | Diff %   | Status         
--------------------------------------------------------------------------------
2026-08-15   | Instagram  | Reel     | 628.0    | 628.0    | +0.0%    | ✅ Normal (New) 
2026-08-16   | Youtube    | Video    | 927.0    | 628.0    | -47.6%   | ✅ Normal (New) 
2026-08-18   | X          | Tweet    | 445.0    | 777.5    | +42.8%   | ⚠️ DROP ALERT (New)
2026-08-19   | Tiktok     | Video    | 920.0    | 666.7    | -38.0%   | ✅ Normal (New) 
2026-08-20   | Linkedin   | Post     | 445.0    | 730.0    | +39.0%   | ✅ Normal (New) 
2026-08-22   | Instagram  | Reel     | 104.0    | 673.0    | +84.5%   | ⚠️ DROP ALERT (New)
================================================================================
```

---

## 📝 Input Log Format (`sample_posts.json`)

Maintain a local JSON array of post entries:
```json
[
  {
    "date": "2026-08-20",
    "platform": "instagram",
    "post_type": "reel",
    "likes": 450,
    "comments": 32,
    "views": 8200
  }
]
```

### Fields:
- `date` *(string, required)*: YYYY-MM-DD format.
- `platform` *(string, required)*: Free-text label (e.g. `instagram`, `youtube`, `x`, `tiktok`).
- `post_type` *(string, required)*: Free-text label (e.g. `reel`, `video`, `tweet`, `post`).
- `likes` *(number, required)*: Number of likes.
- `comments` *(number, required)*: Number of comments.
- `views` *(number, optional)*: Views/impressions count (set `null` or omit if unavailable).

---

## 🧮 Engagement Scoring Formula

$$\text{Engagement Score} = \text{likes} + (\text{comments} \times 3.0) + (\text{views} \times 0.01)$$

- **Comments (3.0x weight)**: Weighted heavier because comments reflect deeper engagement and higher intent.
- **Views (0.01x weight)**: Weighted lighter because video/reel view counts are typically orders of magnitude higher.

### Rolling Average Baseline
- Trailing window of $N$ previous posts (default: 5).
- **Excludes the target post** being evaluated from its baseline calculation to prevent skewing.
- Flagged as `is_underperforming = True` if the score drops more than **40%** below the trailing average.

---

## ⚙️ Configuration (`.env`)

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

| Variable | Default | Description |
| :--- | :--- | :--- |
| `POSTS_LOG_PATH` | `examples/sample_posts.json` | Path to your post log file |
| `ROLLING_WINDOW_SIZE` | `5` | Number of trailing posts in baseline window |
| `UNDERPERFORM_THRESHOLD_PERCENT` | `40.0` | Drop threshold percentage to trigger alert |
| `TELEGRAM_BOT_TOKEN` | *(optional)* | Telegram Bot Token for push alerts |
| `TELEGRAM_CHAT_ID` | *(optional)* | Telegram Chat ID for push alerts |

---

## 🧪 Running Tests

Run the full test suite with `pytest`:
```bash
python3 -m pytest -v
```
