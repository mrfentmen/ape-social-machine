"""Instagram schedule queue + runner — Google Drive as the video host.

No ngrok, no local server, no staging. Videos live in Drive
(gdrive1:blitz-videos/), each has a public direct URL, Instagram fetches
from Google's servers directly.

Queue file: schedule_queue.json — one entry per scheduled reel:
    {
      "file": "blitz-53.mp4",          // filename in gdrive1:blitz-videos/
      "caption": "test 1",
      "account": "blitztheape",
      "at": "2026-09-17T20:05:00Z",    // ISO UTC — when it should POST
      "delete_from_drive": true,       // delete from Drive after successful publish
      "posted": false,
      "posted_at": null,
      "ig_media_id": null,
      "error": null
    }

Usage:
    python ig_scheduler.py add --at "2026-09-17T20:05:00Z" --file blitz-53.mp4 \
        --caption "test 1" [--account blitztheape] [--keep-drive]
    python ig_scheduler.py list
    python ig_scheduler.py run          # post everything due (launchd/cron every 5 min)
    python ig_scheduler.py run --dry    # show what WOULD fire now
    python ig_scheduler.py link         # (re)build drive_urls.json for all files

Requires: rclone remote gdrive1, videos uploaded to gdrive1:blitz-videos/,
public links created (python ig_scheduler.py link does that).
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

import requests

RCLONE = "/Users/dtaxk/.local/bin/rclone"  # launchd has no PATH; absolute path required

HERE = os.path.dirname(os.path.abspath(__file__))
QUEUE_FILE = os.path.join(HERE, "schedule_queue.json")
# accounts.json sits next to this script in the repo (flattened layout);
# the original Mac layout kept it in a subfolder - support both.
_cand = [os.path.join(HERE, "accounts.json"),
         os.path.join(HERE, "instagram", "accounts.json")]
ACCOUNTS_FILE = next((p for p in _cand if os.path.exists(p)), _cand[0])
URLS_FILE = os.path.join(HERE, "drive_urls.json")
DRIVE_REMOTE = "gdrive1:blitz-videos"


def load_queue():
    if os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE) as f:
            return json.load(f)
    return []


def save_queue(q):
    with open(QUEUE_FILE, "w") as f:
        json.dump(q, f, indent=2)


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def direct_url(fname):
    with open(URLS_FILE) as f:
        urls = json.load(f)
    if fname not in urls:
        raise RuntimeError(f"{fname} not in drive_urls.json — run: python ig_scheduler.py link")
    return urls[fname]["direct"]


def post_reel(account, video_url, caption):
    with open(ACCOUNTS_FILE) as f:
        a = json.load(f)[account]
    token, user_id, host = a["access_token"], a["user_id"], a["api_host"]
    # Cloud override (GitHub Actions): secrets beat the file. accounts.json in
    # the repo holds placeholders; real creds come from env.
    token = os.getenv("IG_ACCESS_TOKEN") or token
    user_id = os.getenv("IG_USER_ID") or user_id
    if not (isinstance(host, str) and host.startswith("graph.")):
        host = os.getenv("IG_API_HOST") or "graph.instagram.com"

    r = requests.post(
        f"https://{host}/{user_id}/media",
        data={"media_type": "REELS", "video_url": video_url, "caption": caption,
              "share_to_feed": "true", "access_token": token},
        timeout=120,
    )
    if r.status_code != 200:
        raise RuntimeError(f"container failed: {r.text[:200]}")
    cid = r.json()["id"]

    for _ in range(60):
        s = requests.get(f"https://{host}/{cid}",
                         params={"fields": "status_code", "access_token": token},
                         timeout=30).json()
        if s.get("status_code") == "FINISHED":
            break
        if s.get("status_code") == "ERROR":
            raise RuntimeError(f"container errored: {s}")
        time.sleep(5)

    pub = requests.post(
        f"https://{host}/{user_id}/media_publish",
        data={"creation_id": cid, "access_token": token},
        timeout=60,
    )
    if pub.status_code != 200:
        raise RuntimeError(f"publish failed: {pub.text[:200]}")
    return pub.json()["id"]


def delete_from_drive(fname):
    r = subprocess.run([RCLONE, "deletefile", f"{DRIVE_REMOTE}/{fname}"],
                       capture_output=True, text=True, timeout=120)
    if r.returncode == 0:
        print(f"  deleted from Drive: {fname}")
        # drop from urls map too
        if os.path.exists(URLS_FILE):
            with open(URLS_FILE) as f:
                urls = json.load(f)
            urls.pop(fname, None)
            with open(URLS_FILE, "w") as f:
                json.dump(urls, f, indent=2)
        return True
    print(f"  Drive delete FAILED: {r.stderr[-200:]}")
    return False


def cmd_add(args):
    q = load_queue()
    q.append({
        "file": args.file,
        "caption": args.caption,
        "account": args.account,
        "at": args.at,
        "delete_from_drive": not args.keep_drive,
        "posted": False,
        "posted_at": None,
        "ig_media_id": None,
        "error": None,
    })
    save_queue(q)
    print(f"Scheduled: {args.caption} at {args.at} as {args.account} ({args.file})")


def cmd_list(_args):
    q = load_queue()
    if not q:
        print("Queue is empty.")
        return
    for i, item in enumerate(q):
        if item.get("posted"):
            status = "posted"
        elif item.get("error"):
            status = "ERROR"
        else:
            status = "pending"
        print(f"{i}: [{status}] {item['at']} | {item['account']} | {item['file']} | {item['caption'][:40]}")


def cmd_link(_args):
    """(Re)create public links for every file in Drive, rebuild drive_urls.json."""
    files = subprocess.run([RCLONE, "lsf", f"{DRIVE_REMOTE}/", "--files-only"],
                           capture_output=True, text=True).stdout.split()
    print(f"{len(files)} files in Drive")
    urls = {}
    if os.path.exists(URLS_FILE):
        with open(URLS_FILE) as f:
            urls = json.load(f)
    for i, f in enumerate(files):
        if f in urls and urls[f].get("file_id"):
            continue  # already linked
        r = subprocess.run([RCLONE, "link", f"{DRIVE_REMOTE}/{f}"],
                           capture_output=True, text=True)
        page = r.stdout.strip()
        fid = page.split("id=")[-1] if "id=" in page else ""
        urls[f] = {"page": page, "file_id": fid,
                   "direct": f"https://drive.google.com/uc?export=download&id={fid}"}
        if (i + 1) % 10 == 0:
            print(f"  linked {i+1}/{len(files)}")
    with open(URLS_FILE, "w") as f:
        json.dump(urls, f, indent=2)
    print(f"drive_urls.json written: {len(urls)} entries")


def cmd_run(args):
    q = load_queue()
    now = datetime.now(timezone.utc)
    fired = 0
    max_posts = getattr(args, "max", None)
    for item in q:
        if max_posts is not None and fired >= max_posts:
            print(f"cap reached ({max_posts} per run) - remaining items wait for next tick")
            break
        if item.get("posted") or item.get("error"):
            continue
        due = datetime.fromisoformat(item["at"].replace("Z", "+00:00"))
        if not args.dry and due > now:
            continue
        if args.dry:
            print(f"[dry] would post: {item['caption']} ({item['at']})")
            continue
        try:
            url = direct_url(item["file"])
            mid = post_reel(item["account"], url, item["caption"])
            item["posted"] = True
            item["posted_at"] = now_iso()
            item["ig_media_id"] = mid
            print(f"POSTED: {item['caption']} -> media {mid}")
            if item.get("delete_from_drive"):
                delete_from_drive(item["file"])
            fired += 1
        except Exception as e:  # noqa: BLE001
            item["error"] = str(e)
            print(f"FAILED: {e}")
        time.sleep(10)  # gentle spacing between posts
    save_queue(q)
    print(f"Done. Fired: {fired}")


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    add = sub.add_parser("add")
    add.add_argument("--at", required=True, help="ISO UTC time, e.g. 2026-09-17T20:05:00Z")
    add.add_argument("--file", required=True, help="filename in gdrive1:blitz-videos/")
    add.add_argument("--caption", required=True)
    add.add_argument("--account", default="blitztheape")
    add.add_argument("--keep-drive", action="store_true", help="do NOT delete from Drive after posting")
    sub.add_parser("list").set_defaults(func=cmd_list)
    sub.add_parser("link").set_defaults(func=cmd_link)
    run = sub.add_parser("run")
    run.add_argument("--dry", action="store_true")
    run.add_argument("--max", type=int, default=None,
                     help="cap posts per invocation (cloud runs use 3)")
    run.set_defaults(func=cmd_run)
    add.set_defaults(func=cmd_add)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
