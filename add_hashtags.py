#!/usr/bin/env python3
"""Add hashtags to Blitz X + Bluesky drafts (idempotent, re-runnable).

Rules per post:
  - Any previous trailing tag line is stripped first (so re-runs re-tag).
  - New tag line: #AskApe FIRST + up to 2 discovery tags, via
    blitz_pools.pick_tags.
  - Budget: X limit 280, Bluesky 300; tags appended as base + "\\n\\n" + tags.
  - Must pass humanize_rules.validate_human; falls back to brand-only tag.
  - If even that doesn't fit or fails, the post is left clean and untagged.

Drafts only. Nothing is posted or scheduled by this script.
"""

import json
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from blitz_pools import BRAND_TAGS, pick_tags  # noqa: E402
from humanize_rules import validate_human  # noqa: E402

FILES = ["drafts_bulk.json", "drafts_bulk2.json", "drafts_bulk3.json",
         "drafts_bulk4.json", "drafts_bulk5.json", "drafts_x_linkedin.json"]
LIMITS = {"x": 280, "bluesky": 300}
BRAND = BRAND_TAGS[0]  # "#AskApe"
TAG_LINE_RE = re.compile(r"\n\n(#[A-Za-z0-9]+(?: #[A-Za-z0-9]+)*)\s*$")


def strip_tag_line(text: str) -> str:
    """Remove a trailing tag line from an earlier run."""
    m = TAG_LINE_RE.search(text)
    if m:
        return text[:m.start()].rstrip()
    return text


def main():
    grand = {"x": 0, "bluesky": 0}   # tagged
    skipped = {"x": 0, "bluesky": 0}
    for fn in FILES:
        path = os.path.join(HERE, fn)
        if not os.path.exists(path):
            print(f"skip (missing): {fn}")
            continue
        with open(path) as f:
            data = json.load(f)
        changed = False
        for plat in ("x", "bluesky"):
            limit = LIMITS[plat]
            for post in data.get(plat, []):
                base = strip_tag_line(post["text"])
                budget = limit - len(base) - 2  # minus "\n\n" separator
                rng = random.Random(f"tags-{fn}-{post['id']}")
                tags = pick_tags(rng, plat, budget)
                new = f"{base}\n\n{tags}" if tags else base
                if tags and (len(new) > limit or validate_human(new)["ok"] is False):
                    # fall back to brand tag only
                    if len(BRAND) <= budget:
                        cand = f"{base}\n\n{BRAND}"
                        if len(cand) <= limit and validate_human(cand)["ok"]:
                            tags, new = BRAND, cand
                if tags and (len(new) > limit or validate_human(new)["ok"] is False):
                    new = base  # give up on tags, keep clean text
                    tags = ""
                if new != post["text"]:
                    post["text"] = new
                    changed = True
                post["tags"] = bool(tags)
                if tags:
                    grand[plat] += 1
                else:
                    skipped[plat] += 1
                    print(f"  !! untagged: {fn}#{post['id']} ({len(base)}/{limit})")
        if changed:
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
        print(f"{fn}: done (changed={changed})")
    print("\nSummary:")
    for plat in ("x", "bluesky"):
        print(f"  {plat}: {grand[plat]} tagged, {skipped[plat]} untagged")


if __name__ == "__main__":
    main()
