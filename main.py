# ---
# name: engagement-drop-alert
# description: Platform-agnostic, zero-API social media post performance monitor. Calculates trailing rolling averages of engagement, detects significant performance drops, and sends Telegram push alerts with dynamic AI recommendations.
# metadata:
#   version: 0.1.0
#   status: released
#   rote_version: 0.78.0
#   kind: atomic
#   flow_type: sequential
#   execution_model: legacy
#   requires_sessions: false
# ---

"""Main entrypoint for Rote Play: Engagement Drop Alert."""

import os
import sys

root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from play.main import main

if __name__ == "__main__":
    main()
