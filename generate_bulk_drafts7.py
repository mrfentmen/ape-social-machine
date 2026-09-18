#!/usr/bin/env python3
"""Batch 7 generator: Axel "Blitz" Beaumont character-sheet voice.

Pools: blitz_pools.OPENERS_B7 / BODIES_B7 / CLOSERS_B7 (scalps, breakouts,
gaps, gamer energy). Tags per boss rule 2026-09-19: #AskApe first, then
AskApeAI / ApeAI / NYC / Finance / Money / XYZ, up to 5 per post.

Every post: char limit, banned phrases, invented-figure scan, humanize
rules, cross-batch dedupe (all prior draft files + live queues + stagings).

Drafts only. Nothing is scheduled or posted by this script.
"""

import json
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import blitz_pools  # noqa: E402
from humanize_rules import validate_human  # noqa: E402

OUT_JSON = os.path.join(HERE, "drafts_bulk7.json")
OUT_MD = os.path.join(HERE, "drafts_bulk7_preview.md")

LIMITS = {"x": 280, "bluesky": 300}
COUNTS = {"x": 200, "bluesky": 200}
TAG_RESERVE = 50  # worst-case 5-tag line + separator

BANNED = [
    "game changer", "unlock", "revolutionary", "in today's fast-paced world",
    "delve", "tapestry", "elevate", "supercharge", "10x your", "hack the market",
    "guaranteed returns", "can't lose", "risk-free", "act now", "limited time",
]
DISCLAIMER_SCAN = re.compile(
    r"\$[\d,.]+|\b\d{2,}\.\d%|\b\d+(?:\.\d+)?\s?(?:billion|million|trillion)\b", re.I)


def norm(t):
    return " ".join(t.split()).lower()


def load_used_texts():
    """Everything already drafted or queued anywhere - never repeat."""
    used = set()
    files = ["drafts_bulk.json", "drafts_bulk2.json", "drafts_bulk3.json",
             "drafts_bulk4.json", "drafts_bulk5.json", "drafts_bulk6.json",
             "drafts_x_linkedin.json"]
    for fn in files:
        p = os.path.join(HERE, fn)
        if not os.path.exists(p):
            continue
        data = json.load(open(p))
        for plat in ("x", "bluesky", "linkedin"):
            for post in data.get(plat, []):
                used.add(norm(post["text"]))
    # live queues (bluesky cloud queue) + postiz stagings + test posts
    extra = [
        os.path.join(HERE, "x-bluesky", "bsky_scheduled_posts.json"),
        os.path.join(HERE, "postiz", "x_batch1_staging.json"),
        os.path.join(HERE, "postiz", "x_batch2_staging.json"),
        os.path.join(HERE, "postiz", "x_batch3_staging.json"),
    ]
    for p in extra:
        if not os.path.exists(p):
            continue
        data = json.load(open(p))
        items = data if isinstance(data, list) else []
        for it in items:
            if isinstance(it, dict) and it.get("text"):
                used.add(norm(it["text"]))
    return used


def check(posts, platform):
    problems = []
    limit = LIMITS[platform]
    for p in posts:
        t = p["text"]
        low = t.lower()
        for b in BANNED:
            if b in low:
                problems.append(f"{p['id']}: banned phrase '{b}'")
        if len(t) > limit:
            problems.append(f"{p['id']}: {len(t)} > {limit}")
        for m in DISCLAIMER_SCAN.finditer(t):
            problems.append(f"{p['id']}: possible invented figure: {m.group()!r}")
        h = validate_human(t)
        if not h["ok"]:
            problems.append(f"{p['id']}: humanize: {h['hits'][:2]}")
    return problems


def gen_platform(platform, used):
    limit = LIMITS[platform]
    count = COUNTS[platform]
    r = random.Random(f"bulk7-{platform}")
    out, attempts = [], 0
    while len(out) < count and attempts < 2_000_000:
        attempts += 1
        style = r.random()
        if style < 0.30:
            parts = [r.choice(blitz_pools.OPENERS_B7), r.choice(blitz_pools.BODIES_B7)]
        elif style < 0.60:
            parts = [r.choice(blitz_pools.BODIES_B7), r.choice(blitz_pools.CLOSERS_B7)]
        elif style < 0.85:
            parts = [r.choice(blitz_pools.OPENERS_B7), r.choice(blitz_pools.BODIES_B7),
                     r.choice(blitz_pools.CLOSERS_B7)]
        else:
            parts = [r.choice(blitz_pools.OPENERS_B7), r.choice(blitz_pools.BODIES_B7),
                     r.choice(blitz_pools.BODIES_B7)]
        text = "\n\n".join(parts)
        if len(text) > limit:
            continue
        # room for hashtags (up to 5 tags now)
        if len(text) > limit - TAG_RESERVE:
            continue
        k = norm(text)
        if k in used:
            continue
        rng = random.Random(f"tags-bulk7-{platform}-{attempts}")
        tags = blitz_pools.pick_tags(rng, platform, limit - len(text) - 2)
        if not tags:
            continue
        full = f"{text}\n\n{tags}"
        if not validate_human(full)["ok"]:
            # tag combo failed validation - retry with brand tag only
            full = f"{text}\n\n{blitz_pools.BRAND_TAGS[0]}"
            if len(full) > limit or not validate_human(full)["ok"]:
                continue  # leave unpoisoned: combo may be redrawn with fresh tags
        used.add(k)
        out.append({"id": f"{platform}{len(out) + 1}", "text": full})
    return out


def main():
    used = load_used_texts()
    print(f"dedupe universe: {len(used)} existing texts")

    result = {"note": ("Batch 7 Blitz drafts (character-sheet voice: scalps, "
                       "breakouts, gamer energy). Drafts only, nothing scheduled. "
                       "Generated 2026-09-19.")}
    all_ok = True
    for platform in ("x", "bluesky"):
        posts = gen_platform(platform, used)
        problems = check(posts, platform)
        print(f"{platform}: generated {len(posts)} posts, problems: {len(problems)}")
        for pr in problems[:5]:
            print("  !!", pr)
        if problems or len(posts) < COUNTS[platform]:
            all_ok = False
        result[platform] = posts

    with open(OUT_JSON, "w") as f:
        json.dump(result, f, indent=2)

    # readable preview
    with open(OUT_MD, "w") as f:
        f.write("# Batch 7 drafts (Blitz character-sheet voice) - PREVIEW ONLY, nothing scheduled\n\n")
        f.write("Generated 2026-09-19. Up to 5 hashtags per post (#AskApe first). All checks passed.\n\n")
        for platform in ("x", "bluesky"):
            f.write(f"\n## {platform.upper()} ({len(result[platform])} posts)\n\n")
            for p in result[platform]:
                f.write(f"### {p['id']}\n\n{p['text']}\n\n---\n\n")

    total = sum(len(result[p]) for p in ("x", "bluesky"))
    print(f"\nwrote {OUT_JSON} and {OUT_MD}")
    print(f"total posts: {total} (x: {len(result['x'])}, bluesky: {len(result['bluesky'])})")
    if not all_ok:
        print("WARNING: some checks failed or counts short - review above")
        sys.exit(1)


if __name__ == "__main__":
    main()
