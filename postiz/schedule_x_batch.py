#!/usr/bin/env python3
"""Schedule staged X posts (x_batch1_staging.json) via Postiz.

Target: Axel Beaumont X integration ONLY (cmu63e4kz05j5nl0y88yzl0ip).
Boss accounts are never touched.

Usage:
  python3 schedule_x_batch.py show [--file F]     # print the plan, call nothing
  python3 schedule_x_batch.py test [--file F]     # schedule ONLY the first pending post
  python3 schedule_x_batch.py all [--file F] [--chunk N]  # schedule everything pending, N per call (default 40)
"""

import asyncio
import html
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from postiz_mcp import MCP_URL, get_token  # noqa: E402

STAGING = os.path.join(HERE, "x_batch1_staging.json")
SCHEDULED_MARKER = os.path.join(HERE, "x_batch1_scheduled.json")
X_INTEGRATION_ID = "cmu63e4kz05j5nl0y88yzl0ip"  # Axel Beaumont (pinned)
IS_PREMIUM = False


def text_to_html(text: str) -> str:
    return "".join(f"<p>{html.escape(par)}</p>" for par in text.split("\n\n"))


async def schedule(posts, integration_id):
    from mcp import ClientSession
    from mcp.client.streamable_http import streamablehttp_client

    social = []
    for p in posts:
        social.append({
            "integrationId": integration_id,
            "isPremium": IS_PREMIUM,
            "date": p["at_utc"],
            "shortLink": False,
            "type": "schedule",
            "postsAndComments": [{"content": text_to_html(p["text"]), "attachments": []}],
            "settings": [
                {"key": "post_type", "value": "post"},
                {"key": "who_can_reply_post", "value": "everyone"},
            ],
        })
    tok = get_token()
    async with streamablehttp_client(
        MCP_URL, headers={"Authorization": f"Bearer {tok}"}
    ) as (read, write, _sid):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(
                "integrationSchedulePostTool", arguments={"socialPost": social}
            )
            out = []
            for item in result.content:
                if getattr(item, "type", "") == "text":
                    out.append(item.text)
                else:
                    out.append(f"[non-text: {getattr(item, 'type', '?')}]")
            return "\n".join(out), getattr(result, "isError", False)


def load_done():
    if os.path.exists(SCHEDULED_MARKER):
        with open(SCHEDULED_MARKER) as f:
            return set(json.load(f))
    return set()


def save_done(done):
    with open(SCHEDULED_MARKER, "w") as f:
        json.dump(sorted(done), f, indent=2)


def parse_args():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["show", "test", "all"])
    ap.add_argument("--file", default=None, help="staging file (default: x_batch1_staging.json)")
    ap.add_argument("--chunk", type=int, default=40)
    return ap.parse_args()


def staging_path(file_arg):
    name = file_arg or "x_batch1_staging.json"
    if os.path.sep not in name and not name.endswith(".json"):
        name += "_staging.json"
    return os.path.join(HERE, name)


def marker_path(file_arg):
    base = os.path.basename(staging_path(file_arg)).replace("_staging.json", "")
    return os.path.join(HERE, f"{base}_scheduled.json")


def main():
    args = parse_args()
    STAGING = staging_path(args.file)
    SCHEDULED_MARKER = marker_path(args.file)
    with open(STAGING) as f:
        posts = json.load(f)
    done = load_done()

    if args.mode == "show":
        for p in posts:
            mark = "DONE" if p["source"] in done else "todo"
            print(f"[{mark}] {p['at_local'][:16]} | {p['text'][:70].replace(chr(10), ' / ')}")
        print(f"\ntarget: Axel Beaumont X only ({X_INTEGRATION_ID}); "
              f"todo: {sum(1 for p in posts if p['source'] not in done)}")
        return

    todo = [p for p in posts if p["source"] not in done]
    if args.mode == "test":
        todo = todo[:1]
    if not todo:
        print("nothing to schedule (all done)")
        return
    total = len(todo)
    print(f"scheduling {total} post(s) to Axel Beaumont X ({X_INTEGRATION_ID}) in "
          f"chunks of {args.chunk}...")

    sent = 0
    for start in range(0, total, args.chunk):
        chunk = todo[start:start + args.chunk]
        for p in chunk:
            print(f"  {p['at_utc']} | {p['text'][:60].replace(chr(10), ' / ')}")
        out, is_err = asyncio.run(schedule(chunk, X_INTEGRATION_ID))
        print(out)
        if is_err or '"errors"' in out or 'must be' in out or 'Required' in out:
            print(f"TOOL REPORTED ERROR at chunk starting {start} - stopping, "
                  f"{sent} marked done so far")
            for p in chunk:
                done.discard(p["source"])
            save_done(done)
            sys.exit(1)
        for p in chunk:
            done.add(p["source"])
        save_done(done)
        sent += len(chunk)
        print(f"--- chunk done: {sent}/{total} scheduled ---")
    print(f"marked {sent} scheduled")


if __name__ == "__main__":
    main()
