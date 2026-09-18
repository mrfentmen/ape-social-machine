#!/usr/bin/env python3
"""YouTube daily batch uploader (cloud-safe).

Picks the next N unused finished videos, spreads their publish times over
the next 3 days between 10:00 and 17:00 US Eastern, uploads each via the
poster, and records what was uploaded in yt_uploaded_history.json.

Schedule shape (per boss, 2026-09-19): day+1 gets 3, day+2 gets 4,
day+3 gets 3 for a 10-video day. Publish hours are spread evenly across
10:00 to 17:00 ET within each day, so publish days build up unevenly
(some 6, some 9) as daily batches stack.

Videos come from a local folder (Mac) or, on GitHub, are downloaded from
Google Drive using drive_urls.json (set YT_VIDEOS_DIR to a temp dir).

Usage:
    python3 yt_daily_batch.py --count 10 --dry-run
    python3 yt_daily_batch.py --count 10
"""

import argparse
import json
import os
import subprocess
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from poster_youtube import upload_video  # noqa: E402

FINISHED_DIR = os.path.expanduser("~/ape-gtm/ugc/blitz/finished")
DRIVE_URLS_CANDIDATES = [
    os.path.join(HERE, "drive_urls.json"),  # repo copy (GitHub runner)
    os.path.expanduser("~/Desktop/ai-video-posters/drive_urls.json"),  # Mac
]
HISTORY = os.path.join(HERE, "yt_uploaded_history.json")
CAPTIONS = os.path.join(HERE, "yt_caption_bank.json")

VIDEOS_PER_DAY = 10
DAYS_AHEAD = 3
SHAPE = [3, 4, 3]  # day+1, day+2, day+3
ET_OFFSET = timedelta(hours=-4)  # EDT (UTC-4); change to -5 in winter


def drive_urls_path():
    for p in DRIVE_URLS_CANDIDATES:
        if os.path.exists(p):
            return p
    return DRIVE_URLS_CANDIDATES[0]


def load_json(path):
    with open(path) as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def video_num(name):
    """blitz-52.mp4 -> 52 (stem digits only; the mp4 '4' must not leak in)."""
    stem = os.path.splitext(name)[0]
    digits = "".join(ch for ch in stem if ch.isdigit())
    return int(digits) if digits else None


def load_history():
    """Build the used-video set from local history + what is already live.
    Everything at or below the highest blitz number ever uploaded counts as
    used (sorted order = chronological numbering)."""
    history = load_json(HISTORY) if os.path.exists(HISTORY) else []
    used_nums = set()
    for h in history:
        n = video_num(h.get("video", ""))
        if n is not None:
            used_nums.add(n)
    # videos known to be already used on the channel (uploaded before this
    # tool existed): batch 1 = 58/59/60, earlier manual batch = 52/55/56
    used_nums.update([52, 55, 56, 58, 59, 60])
    if used_nums:
        high = max(used_nums)
        used_nums.update(range(1, high + 1))
    return used_nums


def next_video_number(used_nums):
    """Next unused blitz files, lowest number first (blitz-N.mp4)."""
    candidates = []
    for fn in sorted(os.listdir(FINISHED_DIR)):
        if not fn.lower().endswith(".mp4"):
            continue
        n = video_num(fn)
        if n is not None and n not in used_nums:
            candidates.append((n, fn))
    candidates.sort()
    return [fn for _, fn in candidates]


def get_video(local_path, name, videos_dir):
    """Return a local file path, downloading from Drive if needed."""
    if os.path.exists(local_path):
        return local_path
    os.makedirs(videos_dir, exist_ok=True)
    dpath = drive_urls_path()
    urls = load_json(dpath) if os.path.exists(dpath) else {}
    url = urls.get(name) or urls.get(name.rsplit(".", 1)[0])
    if not url:
        raise FileNotFoundError(f"no local file and no drive url for {name}")
    dest = os.path.join(videos_dir, name)
    print(f"  downloading from Drive: {name}")
    urllib.request.urlretrieve(url, dest)
    return dest


def build_schedule(count):
    """Spread `count` videos over the next DAYS_AHEAD days, 10:00-17:00 ET."""
    now = datetime.now(timezone.utc) + ET_OFFSET
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    per_day = []
    remaining = count
    for i in range(DAYS_AHEAD):
        n = SHAPE[i] if i < len(SHAPE) else 3
        n = min(n, remaining)
        per_day.append(n)
        remaining -= n
    times = []
    for day_idx, n in enumerate(per_day):
        day = today + timedelta(days=day_idx + 1)
        start_hour, end_hour = 10, 17  # ET window
        if n == 1:
            hours = [10]
        else:
            step = (end_hour - start_hour) / (n - 1)
            hours = [round(start_hour + step * i) for i in range(n)]
        seen = set()
        for h in hours:
            while h in seen:
                h += 1
            seen.add(h)
            et = day.replace(hour=h, minute=0)
            utc = et - ET_OFFSET
            times.append(utc.strftime("%Y-%m-%dT%H:%M:%SZ"))
    return times


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=VIDEOS_PER_DAY)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--videos-dir", default=os.path.join(HERE, ".yt_tmp"))
    args = ap.parse_args()

    used_nums = load_history()
    captions = load_json(CAPTIONS)["captions"]

    queue = next_video_number(used_nums)[: args.count]
    if not queue:
        print("No unused videos left. Add new videos to finished/ and clear history entries if recycling.")
        return
    print(f"videos to upload: {len(queue)} -> {queue}")

    times = build_schedule(len(queue))
    if args.dry_run:
        for name, t in zip(queue, times):
            print(f"  {name} -> publish {t}")
        print("dry run only, no uploads")
        return

    for i, name in enumerate(queue):
        num = video_num(name)
        cap = captions[(int(num) - 1) % len(captions)] if num else captions[i % len(captions)]
        local = get_video(os.path.join(FINISHED_DIR, name), name, args.videos_dir)
        print(f"[{i + 1}/{len(queue)}] uploading {name} (publish {times[i]})")
        upload_video(
            local,
            title=cap["title"],
            description=cap["description"],
            tags=["askape", "ai", "stocks", "trading", "finance", "shorts"],
            privacy="private",
            publish_at=times[i],
        )
        history.append({
            "video": name,
            "uploaded_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "publish_at": times[i],
            "caption_id": cap["id"],
        })
        save_json(HISTORY, history)

    remaining = len(next_video_number(used_nums | {n for n in (video_num(q) for q in queue) if n is not None}))
    print(f"Done. Uploaded {len(queue)}. Videos remaining unused: {remaining}")


if __name__ == "__main__":
    main()
