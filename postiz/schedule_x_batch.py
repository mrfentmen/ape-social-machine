#!/usr/bin/env python3
"""Schedule staged X posts (x_batch1_staging.json) via Postiz.

Target: Axel Beaumont X integration ONLY (cmu63e4kz05j5nl0y88yzl0ip).
Boss accounts are never touched.

Usage:
  python3 schedule_x_batch.py test      # schedule ONLY the first post
  python3 schedule_x_batch.py all       # schedule every post not yet scheduled
  python3 schedule_x_batch.py show      # print the plan, call nothing
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


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "show"
    with open(STAGING) as f:
        posts = json.load(f)
    done = load_done()

    if mode == "show":
        for p in posts:
            mark = "DONE" if p["source"] in done else "todo"
            print(f"[{mark}] {p['at_local'][:16]} | {p['text'][:70].replace(chr(10), ' / ')}")
        print(f"\ntarget: Axel Beaumont X only ({X_INTEGRATION_ID})")
        return

    todo = [p for p in posts if p["source"] not in done]
    if mode == "test":
        todo = todo[:1]
    if not todo:
        print("nothing to schedule (all done)")
        return
    print(f"scheduling {len(todo)} post(s) to Axel Beaumont X ({X_INTEGRATION_ID})...")
    for p in todo:
        print(f"  {p['at_utc']} | {p['text'][:60].replace(chr(10), ' / ')}")

    out, is_err = asyncio.run(schedule(todo, X_INTEGRATION_ID))
    print(out)
    # Postiz returns validation errors inside the text payload, not via isError.
    if is_err or '"errors"' in out or 'must be' in out or 'Required' in out:
        print("TOOL REPORTED ERROR - nothing marked done")
        # roll back the premature marker from the earlier bad run
        for p in todo:
            done.discard(p["source"])
        save_done(done)
        sys.exit(1)
    for p in todo:
        done.add(p["source"])
    save_done(done)
    print(f"marked {len(todo)} scheduled")


if __name__ == "__main__":
    main()
