"""Build a full-day queue for @blitztheape from drive_urls.json.

40-50 posts/day, spread 08:00-23:00 local time, giving every video its own
caption from caption_bank.json. Captions are one time use: a caption is handed
out once and only returns after every other caption in the bank has been used.
Skips videos already posted (reads schedule_queue.json history and
.uploaded_instagram.json state).

Usage:
    python build_day_queue.py                    # tomorrow, 45 posts
    python build_day_queue.py --posts 40 --date 2026-09-18
    python build_day_queue.py --start-now        # first post 10 min from now
    python build_day_queue.py --recaption        # refresh captions on pending posts only
    python build_day_queue.py --recaption --dry-run

Caption rules (enforced before anything is scheduled): every caption in
caption_bank.json is 200-300 words, carries exactly 5 hashtags (#AskApe +
#AskApeAI plus 3 rotating discovery tags) and stays under Instagram's 2,200
character caption limit.
"""

import argparse
import json
import os
import re
from collections import deque
from datetime import datetime, timedelta, timezone

WORDS_MIN = 200
WORDS_MAX = 300
HASHTAGS = 5
CHAR_LIMIT = 2200

HERE = os.path.dirname(os.path.abspath(__file__))
QUEUE_FILE = os.path.join(HERE, "schedule_queue.json")
URLS_FILE = os.path.join(HERE, "drive_urls.json")
BANK_FILE = os.path.join(HERE, "caption_bank.json")
UPLOADED_STATE = os.path.join(HERE, ".uploaded_instagram.json")


def check_bank(bank):
    """Fail fast if any caption breaks the SEO caption rules."""
    problems = []
    for i, cap in enumerate(bank):
        text = cap.get("text", "")
        title = cap.get("title", f"#{i}")
        words = len(text.split())
        tags = re.findall(r"#\w+", text)
        if not WORDS_MIN <= words <= WORDS_MAX:
            problems.append(f"{title}: {words} words, need {WORDS_MIN}-{WORDS_MAX}")
        if len(tags) != HASHTAGS:
            problems.append(f"{title}: {len(tags)} hashtags, need exactly {HASHTAGS}")
        if len(text) > CHAR_LIMIT:
            problems.append(f"{title}: {len(text)} chars, IG max is {CHAR_LIMIT}")
    if problems:
        for p in problems:
            print("CAPTION BANK ERROR:", p)
        raise SystemExit(
            f"{len(problems)} caption problem(s) in caption_bank.json - fix before scheduling."
        )
    print(f"caption bank OK: {len(bank)} captions, all {WORDS_MIN}-{WORDS_MAX} words, {HASHTAGS} hashtags each")


def assign_captions(bank, items, spent=()):
    """Give every item its own caption, walking items in post order.

    One time use: a caption is handed out once and only comes back after every
    other caption has been used. Captions already spent on posted posts stay out
    of rotation for as long as the bank lasts, so a live caption is never
    repeated while unused ones are still available. If the bank does run out,
    the oldest captions are recycled first.
    """
    spent = set(spent)
    fresh = deque(c["text"] for c in bank if c["text"] not in spent)
    recycled = deque()
    for item in items:
        if fresh:
            text = fresh.popleft()
        elif recycled:
            text = recycled.popleft()
        else:
            raise SystemExit("caption bank is empty - nothing to assign.")
        recycled.append(text)
        item["caption"] = text


def recaption(account=None, dry_run=False):
    """Rewrite captions on PENDING queue items only, one time use per post.

    Posted items are never touched (their caption is the historical record),
    and their captions are treated as already spent.
    """
    if not os.path.exists(QUEUE_FILE):
        print("No queue file yet - nothing to recaption.")
        return
    q = json.load(open(QUEUE_FILE))
    bank = json.load(open(BANK_FILE))["captions"]
    check_bank(bank)

    posted = [it for it in q if it.get("posted")]
    pending = [it for it in q if not it.get("posted")]
    if account:
        pending = [it for it in pending if it.get("account") == account]
    pending.sort(key=lambda it: it.get("at") or "")

    before = [it.get("caption") for it in pending]
    spent = {it.get("caption") for it in posted if it.get("caption")}

    staged = [dict(it) for it in pending]
    assign_captions(bank, staged, spent)
    changed = sum(1 for old, new in zip(before, [s["caption"] for s in staged]) if old != new)

    if not dry_run:
        for item, assigned in zip(pending, staged):
            item["caption"] = assigned["caption"]
        with open(QUEUE_FILE, "w") as f:
            json.dump(q, f, indent=2)

    verb = "would update" if dry_run else "updated"
    print(f"recaption: {len(pending)} pending item(s), {verb} {changed}, "
          f"bank {len(bank)} captions (one time use, {len(spent)} already live)")


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
    p.add_argument("--recaption", action="store_true",
                   help="rewrite captions on pending queue items only (posted items untouched)")
    p.add_argument("--dry-run", action="store_true",
                   help="with --recaption: report what would change without writing")
    args = p.parse_args()

    if args.recaption:
        recaption(args.account, args.dry_run)
        return

    urls = json.load(open(URLS_FILE))
    bank = json.load(open(BANK_FILE))["captions"]
    check_bank(bank)
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
    if 0 < len(available) < args.posts:
        # No queue history to recycle from (fresh checkout): reuse from the top
        # of the pool rather than crashing when Drive holds fewer videos than
        # the requested post count.
        need = args.posts - len(available)
        refill = sorted(urls)
        available = available + (refill * (need // len(refill) + 1))[:need]
        print(f"Still short {need} video(s) — reusing from the top of the pool.")
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
    # Captions already spoken for by anything ahead of these new posts.
    spent = {it.get("caption") for it in q if it.get("caption")}
    new_items = []
    scheduled = []
    for i in range(args.posts):
        fname = available[i]
        at = first + timedelta(minutes=step * i)
        new_items.append({
            "file": fname,
            "account": args.account,
            "at": at.isoformat().replace("+00:00", "Z"),
            "delete_from_drive": args.delete_drive,
            "posted": False,
            "posted_at": None,
            "ig_media_id": None,
            "error": None,
        })
        scheduled.append((fname, at))

    assign_captions(bank, new_items, spent)
    q.extend(new_items)

    with open(QUEUE_FILE, "w") as f:
        json.dump(q, f, indent=2)

    print(f"Scheduled {len(scheduled)} posts for {args.account}:")
    print(f"  window: {args.start_hour:02d}:00-{args.end_hour:02d}:00 UTC-ish, ~every {step} min")
    print(f"  first: {scheduled[0][1].isoformat()}  last: {scheduled[-1][1].isoformat()}")
    print(f"  captions: {len(bank)} in bank, one time use per post")
    print(f"  videos used: {len(available)} of {len(urls)} total in Drive")
    print(f"  delete-from-drive: {'ON' if args.delete_drive else 'OFF (default)'}")


if __name__ == "__main__":
    main()
