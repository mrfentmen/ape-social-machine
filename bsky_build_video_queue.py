#!/usr/bin/env python3
"""Bluesky video queue builder (STAGING ONLY by default).

Adds Blitz video posts to the Bluesky queue: five a day at 07:45, 08:00, 08:15,
08:30 and 08:45 America/New_York. That early block sits ahead of the 15 minute
text cadence (09:00 to 18:45, the window bsky_build_queue.py builds) so nothing
already armed is disturbed and no two posts ever share a minute.

Videos come from the Postiz media manifest (public mp4 URLs), in the same order
as the X and Threads video plans so all three platforms carry the same video on
the same day. Captions come from the unused Bluesky draft pool, so a video post
never repeats text that is already queued, already sent, or used by another
platform's video plan.

The scheduler must support video for these items to post: it uploads the file
with uploadBlob and embeds app.bsky.embed.video.

Usage:
  python3 bsky_build_video_queue.py --days 11              # build staging
  python3 bsky_build_video_queue.py --days 11 --show       # print staging
  python3 bsky_build_video_queue.py --arm                  # copy staging to live
"""

import argparse
import datetime
import json
import os
import subprocess
import sys
import zoneinfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from bsky_build_queue import load_draft_pool, norm, DRAFT_FILES  # noqa: E402

TZ = zoneinfo.ZoneInfo("America/New_York")
STAGING = os.path.join(HERE, "bsky_video_staging.json")
LIVE = os.path.join(HERE, "x-bluesky", "bsky_scheduled_posts.json")
MEDIA_MANIFEST = os.path.join(os.path.dirname(HERE), "poster-and-scheduler", "postiz", "media_library.json")

VIDEOS_PER_DAY = 5
SLOT_MINUTES = [7 * 60 + 45, 8 * 60, 8 * 60 + 15, 8 * 60 + 30, 8 * 60 + 45]  # 07:45 to 08:45 ET


def probe_aspect(path):
    """Return {width, height} from the local file, or None when ffprobe tells us nothing."""
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=width,height", "-of", "csv=p=0", path],
            capture_output=True, text=True, timeout=30,
        )
        parts = (out.stdout or "").strip().split(",")
        if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
            return {"width": int(parts[0]), "height": int(parts[1])}
    except (FileNotFoundError, subprocess.SubprocessError):
        pass
    return None


def load_media(manifest_path):
    if not os.path.exists(manifest_path):
        raise SystemExit(f"no media manifest at {manifest_path} (run upload_local_media.py first)")
    with open(manifest_path) as f:
        media = json.load(f)
    ready = {k: v for k, v in media.items() if v.get("status") == "ready" and v.get("path")}
    if not ready:
        raise SystemExit("media manifest holds no ready items")
    return ready


def used_texts():
    """Texts already in the live queue or staged, everywhere we can see."""
    used = set()
    if os.path.exists(LIVE):
        with open(LIVE) as f:
            for item in json.load(f):
                if item and item.get("text"):
                    used.add(norm(item["text"]))
    for name in ("bsky_video_staging.json",):
        path = os.path.join(HERE, name)
        if os.path.exists(path):
            with open(path) as f:
                for item in json.load(f):
                    used.add(norm(item["text"]))
    return used


def build(days, start, media, local_dir):
    videos = sorted(media)
    pool = load_draft_pool()
    used = used_texts()
    free = [d for d in pool if norm(d["text"]) not in used]

    need = days * VIDEOS_PER_DAY
    if len(videos) < VIDEOS_PER_DAY:
        raise SystemExit(f"only {len(videos)} ready video(s); need {VIDEOS_PER_DAY} for one day")
    if len(free) < VIDEOS_PER_DAY:
        raise SystemExit(f"not enough unused Bluesky drafts: have {len(free)}, need {VIDEOS_PER_DAY}")
    if len(videos) < need or len(free) < need:
        print(f"note: {len(videos)} video(s) and {len(free)} caption(s) is less than {need} slots; "
              f"the plan stops when either runs out")

    now = datetime.datetime.now(TZ)
    plan = []
    for day in range(days):
        date = start + datetime.timedelta(days=day)
        for i, minute in enumerate(SLOT_MINUTES):
            idx = day * VIDEOS_PER_DAY + i
            if idx >= len(videos) or idx >= len(free):
                break
            when = datetime.datetime.combine(date, datetime.time(minute // 60, minute % 60), tzinfo=TZ)
            if when <= now + datetime.timedelta(minutes=2):
                continue
            name = videos[idx]
            text = free[idx]["text"]
            if len(text) > 300:
                raise SystemExit(f"caption for {name} is {len(text)} chars, Bluesky allows 300")
            aspect = probe_aspect(os.path.join(local_dir, name)) or {"width": 1080, "height": 1920}
            plan.append({
                "at_local": when.isoformat(),
                "at": when.astimezone(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
                "text": text,
                "kind": "root",
                "target_uri": None,
                "video_url": media[name]["path"],
                "aspect": aspect,
                "alt": text.split(".")[0][:200],
                "source": f"video:{name}",
                "posted": False,
                "posted_at": None,
                "uri": None,
                "error": None,
            })
    if not plan:
        raise SystemExit("no future slots in that range")
    return plan


def cmd_show():
    if not os.path.exists(STAGING):
        raise SystemExit(f"no staging plan at {STAGING}; build first")
    with open(STAGING) as f:
        plan = json.load(f)
    for p in plan:
        print(f"{p['at_local'][:16]} ET | {p['source']} | {p['text'][:60].replace(chr(10), ' / ')}")
    print(f"\n{len(plan)} staged video post(s). NOTHING IS QUEUED until --arm.")


def cmd_arm():
    if not os.path.exists(STAGING):
        raise SystemExit(f"no staging plan at {STAGING}; build first")
    with open(STAGING) as f:
        plan = json.load(f)
    with open(LIVE) as f:
        live = json.load(f)
    # Matched on normalised text, so a rebuilt plan cannot slip a duplicate past
    # a whitespace or newline difference. This is the check bsky_build_queue.py
    # was missing.
    existing = {(i.get("at"), norm(i.get("text") or "")) for i in live if i}
    added = 0
    for p in plan:
        key = (p["at"], norm(p["text"]))
        if key in existing:
            continue
        live.append({k: v for k, v in p.items() if k not in ("at_local", "source")})
        existing.add(key)
        added += 1
    with open(LIVE, "w") as f:
        json.dump(live, f, indent=2)
    print(f"ARMED: {added} video post(s) copied into {LIVE} "
          f"({len(plan) - added} already present); queue now holds {len(live)}")
    print("The CLOUD scheduler posts these (GitHub Actions, repo")
    print("mrfentmen/ape-social-machine) - that workflow owns Bluesky, so do NOT")
    print("also run a local scheduler or the same queue gets posted twice.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=11)
    ap.add_argument("--start", default=datetime.date.today().isoformat())
    ap.add_argument("--media", default=MEDIA_MANIFEST)
    ap.add_argument("--local-dir", default=os.path.expanduser("~/Desktop/Blitz videos"))
    ap.add_argument("--show", action="store_true")
    ap.add_argument("--arm", action="store_true")
    args = ap.parse_args()

    if args.show:
        return cmd_show()
    if args.arm:
        return cmd_arm()

    try:
        start = datetime.date.fromisoformat(args.start)
    except ValueError:
        raise SystemExit(f"--start must be YYYY-MM-DD, got {args.start!r}")

    plan = build(args.days, start, load_media(args.media), args.local_dir)
    with open(STAGING, "w") as f:
        json.dump(plan, f, indent=2)
    days = sorted({p["at_local"][:10] for p in plan})
    print(f"staged {len(plan)} video post(s): {days[0]} to {days[-1]} "
          f"({VIDEOS_PER_DAY}/day at 07:45-08:45 ET)")
    print(f"videos used: {len({p['source'] for p in plan})} | captions unique: "
          f"{len({p['text'] for p in plan})}")
    print("NOTHING IS QUEUED YET. Review with --show, then arm with --arm.")


if __name__ == "__main__":
    main()
