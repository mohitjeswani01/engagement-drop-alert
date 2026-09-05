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
====================================================================================
 📊 ENGAGEMENT DROP ALERT — SUMMARY REPORT
====================================================================================
 Total Posts in Log: 6
 Newly Checked Posts: 6
 Alerts Dispatched: 0
------------------------------------------------------------------------------------
Date         | Platform   | Type     | Score    | Avg      | % Below Avg  | Status         
------------------------------------------------------------------------------------
2026-08-15   | instagram  | reel     | 628.0    | 628.0    | +0.0%        | ✅ Normal (New) 
2026-08-16   | youtube    | video    | 927.0    | 628.0    | -47.6%       | ✅ Normal (New) 
2026-08-18   | x          | tweet    | 445.0    | 777.5    | +42.8%       | ⚠️ DROP ALERT (New)
2026-08-19   | tiktok     | video    | 920.0    | 666.7    | -38.0%       | ✅ Normal (New) 
2026-08-20   | linkedin   | post     | 445.0    | 730.0    | +39.0%       | ✅ Normal (New) 
2026-08-22   | instagram  | reel     | 104.0    | 673.0    | +84.5%       | ⚠️ DROP ALERT (New)
====================================================================================
```

> **Note on "% Below Avg"**: Positive percentages indicate performance drop below rolling average (+84.5% = 84.5% drop below baseline). Negative percentages indicate performance outperforming baseline (-47.6% = 47.6% above baseline).

---

## 🔍 Step-by-Step Worked Calculation Example

Using real entries from `examples/sample_posts.json`:

### 1. Evaluating Post #6 (`2026-08-22`, Instagram Reel):
- **Metrics**: 80 likes, 4 comments, 1,200 views.

### 2. Calculate Engagement Score:
$$\text{Score} = \text{likes} + (\text{comments} \times 3.0) + (\text{views} \times 0.01)$$
$$\text{Score} = 80 + (4 \times 3.0) + (1200 \times 0.01) = 80 + 12 + 12.0 = \mathbf{104.0}$$

### 3. Calculate Trailing Rolling Average Baseline ($N=5$):
Baseline uses the previous up to 5 posts (indices 0 to 4):
- Post 1 (Instagram): 628.0
- Post 2 (YouTube): 927.0
- Post 3 (X): 445.0
- Post 4 (TikTok): 920.0
- Post 5 (LinkedIn): 445.0

$$\text{Rolling Avg} = \frac{628.0 + 927.0 + 445.0 + 920.0 + 445.0}{5} = \frac{3365.0}{5} = \mathbf{673.0}$$

### 4. Calculate % Below Average & Alert Status:
$$\text{\% Below Avg} = \frac{\text{Rolling Avg} - \text{Score}}{\text{Rolling Avg}} \times 100\% = \frac{673.0 - 104.0}{673.0} \times 100\% = \mathbf{+84.55\%}$$

Since $+84.55\% \ge 40.0\%$ (the default drop threshold), this post is flagged as **`is_underperforming = True`** and triggers a Telegram alert!

---

## 📊 How Do I Get My Post Numbers?

Since this Play is zero-API by design, you manually enter likes, comments, and views from your social media apps. Here is where to find them:

- **Instagram**: Tap **View Insights** directly below your post or reel.
- **YouTube**: Open **YouTube Studio** $\rightarrow$ select video $\rightarrow$ **Analytics** tab.
- **X (Twitter)**: Click the **Analytics icon** (bar chart) at the bottom right of your tweet.
- **TikTok**: Tap **More data / Analytics** at the bottom right of your video.
- **LinkedIn**: Click **View Analytics** at the bottom of your post.

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

## ⚙️ Configuration & CLI Options

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

| Variable | Default | Description |
| :--- | :--- | :--- |
| `POSTS_LOG_PATH` | `examples/sample_posts.json` | Path to your post log file |
| `ROLLING_WINDOW_SIZE` | `5` | Trailing window size $N$ for baseline calculation |
| `UNDERPERFORM_THRESHOLD_PERCENT` | `40.0` | Drop threshold percentage to trigger alert |
| `TELEGRAM_BOT_TOKEN` | *(optional)* | Telegram Bot Token for push alerts |
| `TELEGRAM_CHAT_ID` | *(optional)* | Telegram Chat ID for push alerts |

### CLI Flags

- `--file <path>` / `-f <path>`: Specify custom path to post log JSON file.
- `--force-recheck`: Forces re-evaluation and notification check on **all** posts in the log file, ignoring any pre-existing `"checked": true` flags.

---

## 🧪 Running Tests

Run the full test suite with `pytest`:
```bash
python3 -m pytest -v
```
