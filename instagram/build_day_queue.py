"""Build a full-day queue for @blitztheape from drive_urls.json.

40-50 posts/day, spread 08:00-23:00 local time, rotating caption_bank.json
captions in order. Skips videos already posted (reads schedule_queue.json
history and .uploaded_instagram.json state).

Usage:
    python build_day_queue.py                    # tomorrow, 45 posts
    python build_day_queue.py --posts 40 --date 2026-09-18
    python build_day_queue.py --start-now        # first post 10 min from now
"""

import argparse
import json
import os
import random
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
QUEUE_FILE = os.path.join(HERE, "schedule_queue.json")
URLS_FILE = os.path.join(HERE, "drive_urls.json")
BANK_FILE = os.path.join(HERE, "caption_bank.json")
UPLOADED_STATE = os.path.join(HERE, ".uploaded_instagram.json")


def already_posted():
    """Filenames ever posted (queue history + upload state)."""
    done = set()
    if os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE) as f:
            for item in json.load(f):
                done.add(item.get("file"))
    if os.path.exists(UPLOADED_STATE):
        with open(UPLOADED_STATE) as f:
            done |= set(json.load(f).keys())
    return done


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--posts", type=int, default=45)
    p.add_argument("--date", help="YYYY-MM-DD (default: tomorrow)")
    p.add_argument("--account", default="blitztheape")
    p.add_argument("--start-hour", type=int, default=8)
    p.add_argument("--end-hour", type=int, default=23)
    p.add_argument("--start-now", action="store_true", help="first post ~10 min from now")
    p.add_argument("--delete-drive", action="store_true",
                   help="delete from Drive after posting (default: keep, so reels can be reposted across days)")
    args = p.parse_args()

    urls = json.load(open(URLS_FILE))
    bank = json.load(open(BANK_FILE))["captions"]
    done = already_posted()

    available = [f for f in sorted(urls) if f not in done]
    if len(available) < args.posts:
        # RECYCLE: pool exhausted — refill from already-queued videos,
        # least-recently-posted first (pending-but-unposted ones recycle last).
        history = {}  # file -> posted_at (far-future sentinel for pending)
        if os.path.exists(QUEUE_FILE):
            for item in json.load(open(QUEUE_FILE)):
                history[item["file"]] = item.get("posted_at") or "9999-12-31"
        recycle_pool = [f for f in sorted(urls) if f in history]
        recycle = sorted(recycle_pool, key=history.get)
        need = args.posts - len(available)
        available = available + recycle[:need]
        print(f"Pool exhausted — recycling {need} video(s) (least-recently-posted first).")
    if not available:
        print("No videos at all. Upload some to Drive first.")
        return

    # schedule day
    if args.date:
        day = datetime.fromisoformat(args.date).replace(tzinfo=timezone.utc)
    else:
        day = (datetime.now(timezone.utc) + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0)
    if args.start_now:
        first = datetime.now(timezone.utc) + timedelta(minutes=10)
    else:
        first = day + timedelta(hours=args.start_hour)

    window_min = (args.end_hour - args.start_hour) * 60
    step = window_min // args.posts  # minutes between posts

    q = json.load(open(QUEUE_FILE)) if os.path.exists(QUEUE_FILE) else []
    scheduled = []
    for i in range(args.posts):
        fname = available[i]
        at = first + timedelta(minutes=step * i)
        q.append({
            "file": fname,
            "caption": bank[i % len(bank)]["text"],
            "account": args.account,
            "at": at.isoformat().replace("+00:00", "Z"),
            "delete_from_drive": args.delete_drive,
            "posted": False,
            "posted_at": None,
            "ig_media_id": None,
            "error": None,
        })
        scheduled.append((fname, at))

    with open(QUEUE_FILE, "w") as f:
        json.dump(q, f, indent=2)

    print(f"Scheduled {len(scheduled)} posts for {args.account}:")
    print(f"  window: {args.start_hour:02d}:00-{args.end_hour:02d}:00 UTC-ish, ~every {step} min")
    print(f"  first: {scheduled[0][1].isoformat()}  last: {scheduled[-1][1].isoformat()}")
    print(f"  captions rotate: {len(bank)} in bank")
    print(f"  videos used: {len(available)} of {len(urls)} total in Drive")
    print(f"  delete-from-drive: {'ON' if args.delete_drive else 'OFF (default)'}")


if __name__ == "__main__":
    main()
