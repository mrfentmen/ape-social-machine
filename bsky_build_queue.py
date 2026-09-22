"""Bluesky daily queue builder (STAGING ONLY by default).

Reads Blitz voice drafts from the bulk draft files and builds a posting plan
in bsky_queue_staging.json. It NEVER touches the live scheduler queue
(x-bluesky/bsky_scheduled_posts.json) unless you run it with --arm AND the
staging file exists. Nothing posts from this script itself; posting only
happens if the human runs the scheduler with the live queue armed.

Plan shape (user cadence, Sep 2026):
  Posts every 15 minutes from 09:00 to 18:45 local = 40 posts/day,
  starting tomorrow. Runs in the CLOUD via GitHub Actions (repo
  ape-social-machine); the local scheduler.js must NOT also run, or you
  double-post. Cloud owns Bluesky.

Usage:
  python3 bsky_build_queue.py                  # build staging plan (3 days x 40)
  python3 bsky_build_queue.py --days 7         # longer plan
  python3 bsky_build_queue.py --show           # print current staging plan
  python3 bsky_build_queue.py --arm            # copy staging -> live scheduler queue
  python3 bsky_build_queue.py --disarm         # wipe live scheduler queue (empty [])
"""

import json
import os
import glob
import random
import re
import sys
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
LOCAL_TZ = datetime.now().astimezone().tzinfo

def _draft_sort_key(name):
    """drafts_bulk.json, drafts_bulk2.json ... drafts_bulk11.json in order."""
    m = re.search(r"drafts_bulk(\d*)\.json$", name)
    return int(m.group(1)) if m and m.group(1) else 1


# Every bulk draft file, so new batches are picked up automatically. The old
# hardcoded list stopped at batch 5, which hid batches 6 to 11 from the builder.
DRAFT_FILES = sorted(
    (os.path.basename(p) for p in glob.glob(os.path.join(HERE, "drafts_bulk*.json"))),
    key=_draft_sort_key,
)  # Blitz voice, tagged
STAGING = os.path.join(HERE, "bsky_queue_staging.json")
LIVE = os.path.join(HERE, "x-bluesky", "bsky_scheduled_posts.json")
SENT_LOG = os.path.join(HERE, "x-bluesky", "bsky_posts_sent.txt")

START_HOUR = 9    # first post 09:00 local
END_HOUR = 19     # last slot before 19:00 -> 18:45
STEP_MIN = 15
POSTS_PER_DAY = (END_HOUR - START_HOUR) * 60 // STEP_MIN  # 40


def norm(t):
    return " ".join(t.split()).lower()


# Tags the sent log uses in its four field form, so a text that happens to
# contain " | " is not mistaken for a tagged line.
SENT_LOG_TAGS = ("root", "failed")


def text_from_log_line(line):
    """The post text out of one sent-log line, or None.

    Two writers feed x-bluesky/bsky_posts_sent.txt with different shapes:
      scheduler.js -> "ISO | uri | tag | text"   (tag is root or reply_to=<uri>)
      bluesky.js   -> "ISO | uri | text"        (three fields, no tag)

    The old reader required exactly four fields, so every three field line -
    which is everything the standalone poster ever wrote - was invisible. Those
    texts stayed in the draft pool and could be staged and published a second
    time, which is a repost of copy already live on the account.
    """
    line = (line or "").rstrip("\n")
    if not line:
        return None
    parts = line.split(" | ", 2)          # ISO, uri, remainder
    if len(parts) < 3:
        return None
    rest = parts[2]
    for tag in SENT_LOG_TAGS:
        if rest.startswith(tag + " | "):
            return rest[len(tag) + 3:]
    if rest.startswith("reply_to=") and " | " in rest:
        return rest.split(" | ", 1)[1]
    return rest


def load_sent_texts():
    """Texts already posted to Bluesky (from the sent log)."""
    sent = set()
    if os.path.exists(SENT_LOG):
        with open(SENT_LOG) as f:
            for line in f:
                text = text_from_log_line(line)
                if text:
                    sent.add(norm(text))
    return sent


def load_draft_pool():
    """Bluesky-usable drafts: voice==blitz, <=300 chars, not already posted."""
    sent = load_sent_texts()
    pool = []
    for fn in DRAFT_FILES:
        path = os.path.join(HERE, fn)
        if not os.path.exists(path):
            continue
        with open(path) as f:
            data = json.load(f)
        for p in data.get("bluesky", []):
            # Batches 7 and later carry no voice field, they are Blitz voice by
            # construction. Only reject a draft when it names a different voice.
            if p.get("voice") not in (None, "blitz"):
                continue
            if len(p["text"]) > 300:
                continue
            if norm(p["text"]) in sent:
                continue
            pool.append({"source": fn, "id": p["id"], "text": p["text"]})
    return pool


def build_plan(days: int, start_offset_days: int = 1) -> list:
    pool = load_draft_pool()
    # Never re-stage a draft that is anywhere in the live queue, posted or not.
    # The old condition was `not item.get("posted")`, which excluded only the
    # PENDING queue entries and therefore put already-published copy straight
    # back into the pool - a repost waiting to be armed.
    used_texts = set()
    if os.path.exists(LIVE):
        with open(LIVE) as f:
            for item in json.load(f):
                if item and item.get("text"):
                    used_texts.add(norm(item["text"]))
    existing_staging = []
    if os.path.exists(STAGING):
        with open(STAGING) as f:
            existing_staging = json.load(f)
        for p in existing_staging:
            used_texts.add(norm(p["text"]))
    pool = [d for d in pool if norm(d["text"]) not in used_texts]
    if len(pool) < days * POSTS_PER_DAY:
        raise SystemExit(f"not enough unused drafts: have {len(pool)}, "
                         f"need {days * POSTS_PER_DAY}. Generate more or add files to DRAFT_FILES.")
    r = random.Random(f"bsky-{start_offset_days}-{days}")
    r.shuffle(pool)
    chosen = pool[:days * POSTS_PER_DAY]

    plan = []
    start_day = (datetime.now(LOCAL_TZ) + timedelta(days=start_offset_days)).replace(
        hour=START_HOUR, minute=0, second=0, microsecond=0)
    i = 0
    for day in range(days):
        for slot in range(POSTS_PER_DAY):
            when = start_day + timedelta(days=day,
                                         hours=slot * STEP_MIN // 60,
                                         minutes=(slot * STEP_MIN) % 60)
            d = chosen[i]
            i += 1
            plan.append({
                "at_local": when.isoformat(),
                "at_utc": when.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
                "text": d["text"],
                "source": f"{d['source']}#{d['id']}",
            })
    return plan


def cmd_show():
    if not os.path.exists(STAGING):
        print("No staging plan. Run: python3 bsky_build_queue.py")
        return
    with open(STAGING) as f:
        plan = json.load(f)
    print(f"Staging plan: {len(plan)} posts "
          f"({sum(1 for p in plan if not p.get('queued'))} not yet queued to live)\n")
    for p in plan:
        flag = "QUEUED" if p.get("queued") else "staged "
        print(f"[{flag}] {p['at_local']}  ({p['source']})")
        print(f"   {p['text'][:90].replace(chr(10), ' / ')}...")
    print("\nThis is a STAGING file. Nothing is scheduled until you run --arm.")


def cmd_arm():
    """Copy staging plan into the LIVE scheduler queue (explicit action only)."""
    if not os.path.exists(STAGING):
        raise SystemExit("no staging plan; run: python3 bsky_build_queue.py")
    with open(STAGING) as f:
        plan = json.load(f)
    pending = [p for p in plan if not p.get("queued")]
    if not pending:
        print("All staged posts already queued. Nothing to arm.")
        return
    with open(LIVE) as f:
        live = json.load(f)
    # Match on slot + text so arming twice cannot duplicate the queue. The video
    # builder always checked this; the text builder did not, so a rebuilt staging
    # file re-added every slot it still shared with the live queue.
    existing = {(i.get("at"), norm(i.get("text") or "")) for i in live if i}
    added = 0
    for p in pending:
        key = (p["at_utc"], norm(p["text"]))
        if key in existing:
            continue
        live.append({
            "at": p["at_utc"],
            "text": p["text"],
            "kind": "root",
            "target_uri": None,
            "posted": False,
            "posted_at": None,
            "uri": None,
            "error": None,
        })
        existing.add(key)
        added += 1
    with open(LIVE, "w") as f:
        json.dump(live, f, indent=2)
    for p in plan:
        p["queued"] = True
    with open(STAGING, "w") as f:
        json.dump(plan, f, indent=2)
    print(f"ARMED: {added} new post(s) copied to live scheduler queue {LIVE} "
          f"({len(pending) - added} already present, skipped); queue holds {len(live)}")
    print("The CLOUD scheduler posts these (GitHub Actions, repo")
    print("mrfentmen/ape-social-machine) - that workflow owns Bluesky, so do NOT")
    print("also run a local scheduler or the same queue gets posted twice.")
    print("Preview locally only: cd x-bluesky && node src/scheduler.js --dry")


def cmd_disarm():
    with open(LIVE, "w") as f:
        json.dump([], f, indent=2)
    print(f"DISARMED: live scheduler queue at {LIVE} is now empty. Nothing will fire.")


def main():
    if "--show" in sys.argv:
        return cmd_show()
    if "--disarm" in sys.argv:
        return cmd_disarm()
    if "--arm" in sys.argv:
        return cmd_arm()
    days, start_days = 3, 1
    for i, a in enumerate(sys.argv):
        if a == "--days":
            days = int(sys.argv[i + 1])
        if a == "--start-days":
            start_days = int(sys.argv[i + 1])
    plan = build_plan(days, start_days)

    # Append to staging (dedupe on exact slot+text) so batches accumulate.
    existing = []
    if os.path.exists(STAGING):
        with open(STAGING) as f:
            existing = json.load(f)
    known = {(p["at_local"], norm(p["text"])) for p in existing}
    added = [p for p in plan if (p["at_local"], norm(p["text"])) not in known]
    merged = existing + added
    with open(STAGING, "w") as f:
        json.dump(merged, f, indent=2)
    print(f"staged {len(added)} new posts over {days} days "
          f"(start in {start_days} day(s), {POSTS_PER_DAY}/day, "
          f"every {STEP_MIN}min {START_HOUR}:00-{END_HOUR - 1}:45 local); "
          f"staging now holds {len(merged)}")
    print("NOTHING IS SCHEDULED YET. Review with --show, then arm with --arm when you say go.")


if __name__ == "__main__":
    main()
