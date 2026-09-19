#!/usr/bin/env python3
"""Batch 11 generator: 1000 X + 1000 Bluesky + 600 LinkedIn drafts.

Why this batch is bigger: the shared X/Threads pool was nearly spent. After
the Sep 19-30 Postiz loads and the Threads batches, only a few hundred unused
X texts remained, which is about four days at 60 posts per day plus Threads.
Batch 11 restocks roughly two weeks of X plus Threads and Bluesky coverage.

Rules (same as batches 7 to 10):
- X + Bluesky: Blitz persona (character sheet voice, fresh batch 11 pools).
- LinkedIn: company page voice, plain language, no mascot narrator.
- Hashtags: #AskApe first, up to 5 total, letters only.
- Deduped against every existing draft, queue and staging file we can see.
- humanize_rules.validate_human on every composed post, no dashes anywhere.
- Drafts only: nothing here is scheduled or posted.

Usage:
    python3 generate_bulk_drafts11.py
"""

import glob
import json
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import blitz_pools  # noqa: E402
import blitz_pools_11  # noqa: E402
import skill_li_pools  # noqa: E402
import skill_li_pools_11  # noqa: E402
from humanize_rules import validate_human  # noqa: E402

OUT_JSON = os.path.join(HERE, "drafts_bulk11.json")
OUT_MD = os.path.join(HERE, "drafts_bulk11_preview.md")

LIMITS = {"x": 280, "bluesky": 300, "linkedin": 3000}
COUNTS = {"x": 1000, "bluesky": 1000, "linkedin": 600}
TAG_RESERVE = 50

# Staging lives in the sibling project for the Postiz queues.
EXTERNAL_GLOBS = [
    os.path.join(os.path.dirname(HERE), "poster-and-scheduler", "postiz", "*.json"),
]

BANNED = [
    "game changer", "unlock", "revolutionary", "in today's fast-paced world",
    "delve", "tapestry", "elevate", "supercharge", "10x your", "hack the market",
    "guaranteed returns", "can't lose", "risk-free", "act now", "limited time",
]
FIGURE_SCAN = re.compile(
    r"\$[\d,.]+|\b\d+(?:\.\d+)?\s?%|\b\d+(?:\.\d+)?\s?(?:billion|million|trillion)\b",
    re.I,
)

DISCLAIMER = skill_li_pools.DISCLAIMER if hasattr(skill_li_pools, "DISCLAIMER") else (
    "Educational purposes only. Not financial advice."
)


def norm(text):
    return " ".join(text.split()).lower()


def base_text(text):
    """Post body without the trailing tag line (the cross platform dedupe key)."""
    return re.sub(r"\n\n#.*$", "", text, flags=re.S).strip()


def collect_texts(obj, out):
    """Pull every draft/post string out of a draft or queue file."""
    def add(text):
        # Both the full post and the body without its tag line are dedupe keys:
        # the brand rule is that the body never repeats, even with new tags.
        out.add(norm(text))
        out.add(norm(base_text(text)))

    if isinstance(obj, dict):
        for key in ("x", "bluesky", "linkedin", "captions"):
            for item in obj.get(key, []) or []:
                if isinstance(item, dict):
                    for f in ("text", "caption"):
                        if isinstance(item.get(f), str):
                            add(item[f])
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, dict):
                for f in ("text", "caption"):
                    if isinstance(item.get(f), str):
                        add(item[f])


def load_used_texts():
    """Everything already drafted, queued or staged anywhere we can read."""
    used = set()
    patterns = [
        os.path.join(HERE, "drafts_bulk*.json"),
        os.path.join(HERE, "x-bluesky", "*.json"),
        os.path.join(HERE, "instagram", "*.json"),
        os.path.join(HERE, "postiz", "*.json"),
    ] + EXTERNAL_GLOBS
    files = []
    for pattern in patterns:
        files.extend(glob.glob(pattern))
    for path in sorted(set(files)):
        if path.endswith("package-lock.json"):
            continue
        try:
            with open(path) as f:
                data = json.load(f)
        except (ValueError, OSError):
            continue
        collect_texts(data, used)
    return used


def check(posts, platform):
    problems = []
    limit = LIMITS[platform]
    for p in posts:
        t = p["text"]
        low = t.lower()
        for b in BANNED:
            if b in low:
                problems.append(f"{p['id']}: banned phrase {b!r}")
        if len(t) > limit:
            problems.append(f"{p['id']}: {len(t)} > {limit}")
        m = FIGURE_SCAN.search(t)
        if m:
            problems.append(f"{p['id']}: possible invented figure {m.group()!r}")
        h = validate_human(t)
        if not h["ok"]:
            problems.append(f"{p['id']}: humanize: {h['hits'][:2]}")
        if "#AskApe" not in t:
            problems.append(f"{p['id']}: missing #AskApe")
    return problems


def blitz_parts(r):
    """One composition: fresh batch 11 pools mostly, older sheet pools sometimes."""
    fresh = r.random() < 0.7
    if fresh:
        op, body, close = (
            blitz_pools_11.OPENERS_11,
            blitz_pools_11.BODIES_11,
            blitz_pools_11.CLOSERS_11,
        )
    else:
        use_b9 = r.random() < 0.5
        op = blitz_pools.OPENERS_B9 if use_b9 else blitz_pools.OPENERS_B7
        body = blitz_pools.BODIES_B9 if use_b9 else blitz_pools.BODIES_B7
        close = blitz_pools.CLOSERS_B9 if use_b9 else blitz_pools.CLOSERS_B7
    style = r.random()
    if style < 0.35:
        return [r.choice(op)]
    if style < 0.80:
        return [r.choice(op), r.choice(body)]
    return [r.choice(body), r.choice(close)]


def gen_blitz(platform, used):
    limit = LIMITS[platform]
    count = COUNTS[platform]
    r = random.Random(f"bulk11-{platform}")
    out, attempts = [], 0
    while len(out) < count and attempts < 1_000_000:
        attempts += 1
        text = "\n\n".join(blitz_parts(r))
        if len(text) > limit - TAG_RESERVE:
            continue
        key = norm(text)
        if key in used:
            continue
        tag_rng = random.Random(f"tags-bulk11-{platform}-{attempts}")
        tags = blitz_pools.pick_tags(tag_rng, platform, limit - len(text) - 2)
        if not tags:
            continue
        full = f"{text}\n\n{tags}"
        if not validate_human(full)["ok"]:
            continue
        used.add(key)
        out.append({"id": f"{platform}{len(out) + 1}", "text": full})
    return out


def gen_linkedin(used):
    count = COUNTS["linkedin"]
    r = random.Random("bulk11-linkedin")
    li_tags = ["#AskApe", "#Finance", "#Investing", "#Fintech", "#AskApeAI"]
    alt_tags = ["#AskApe", "#Investing", "#NYC", "#Fintech", "#ApeAI"]
    out, attempts = [], 0
    while len(out) < count and attempts < 500_000:
        attempts += 1
        # 70 percent fresh batch 11 pools, 30 percent the older skill pools.
        if r.random() < 0.7:
            parts = (
                f"{r.choice(skill_li_pools_11.OPENERS_11)}\n\n"
                f"{r.choice(skill_li_pools_11.MID_11)} {r.choice(skill_li_pools_11.BODIES_11)}\n\n"
                f"{r.choice(skill_li_pools_11.CTAS_11)}"
            )
        else:
            parts = (
                f"{r.choice(skill_li_pools.OPENERS)}\n\n"
                f"{r.choice(skill_li_pools.MID)} {r.choice(skill_li_pools.BODIES)}\n\n"
                f"{r.choice(skill_li_pools.CTAS)}"
            )
        body = f"{parts}\n\n{DISCLAIMER}"
        tags = " ".join(li_tags if r.random() < 0.7 else alt_tags)
        full = f"{body}\n\n{tags}"
        if len(full) > LIMITS["linkedin"]:
            continue
        key = norm(body)
        if key in used:
            continue
        if not validate_human(full)["ok"]:
            continue
        used.add(key)
        out.append({"id": f"li{len(out) + 1}", "text": full})
    return out


def pool_self_check():
    """Fail loudly if any pool line breaks the brand rules."""
    problems = []
    groups = {
        "blitz_pools_11.OPENERS_11": blitz_pools_11.OPENERS_11,
        "blitz_pools_11.BODIES_11": blitz_pools_11.BODIES_11,
        "blitz_pools_11.CLOSERS_11": blitz_pools_11.CLOSERS_11,
        "skill_li_pools_11.OPENERS_11": skill_li_pools_11.OPENERS_11,
        "skill_li_pools_11.MID_11": skill_li_pools_11.MID_11,
        "skill_li_pools_11.BODIES_11": skill_li_pools_11.BODIES_11,
        "skill_li_pools_11.CTAS_11": skill_li_pools_11.CTAS_11,
    }
    for name, lines in groups.items():
        for i, line in enumerate(lines):
            h = validate_human(line)
            if not h["ok"]:
                problems.append(f"{name}[{i}]: {h['hits']}")
            low = line.lower()
            for b in BANNED:
                if b in low:
                    problems.append(f"{name}[{i}]: banned phrase {b!r}")
            m = FIGURE_SCAN.search(line)
            if m:
                problems.append(f"{name}[{i}]: possible figure {m.group()!r}")
    return problems


def main():
    pool_problems = pool_self_check()
    print(f"pool self check: {len(pool_problems)} problem(s)")
    for p in pool_problems[:10]:
        print("  !!", p)
    if pool_problems:
        print("fix the pool lines before generating")
        return 1

    used = load_used_texts()
    print(f"dedupe universe: {len(used)} existing texts")

    result = {"note": (
        "Batch 11 drafts: X + Bluesky in Blitz persona voice (fresh batch 11 "
        "pools), LinkedIn in company page voice (plain language). Hashtags on "
        "all. Drafts only, nothing scheduled. Generated 2026-09-18 night, "
        "restock after the Sep 19-30 Postiz and Threads loads."
    )}
    ok = True
    for platform in ("x", "bluesky", "linkedin"):
        posts = gen_linkedin(used) if platform == "linkedin" else gen_blitz(platform, used)
        problems = check(posts, platform)
        print(f"{platform}: generated {len(posts)} posts, problems: {len(problems)}")
        for pr in problems[:5]:
            print("  !!", pr)
        if problems or len(posts) < COUNTS[platform]:
            ok = False
        result[platform] = posts

    with open(OUT_JSON, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    with open(OUT_MD, "w") as f:
        f.write("# Batch 11 drafts (Blitz for X/Bluesky, corporate ape for LinkedIn) PREVIEW ONLY\n\n")
        f.write("Generated 2026-09-18 night. Hashtags on all. Drafts only: nothing scheduled.\n\n")
        for platform in ("x", "bluesky", "linkedin"):
            f.write(f"\n## {platform.upper()} ({len(result[platform])} posts)\n\n")
            for p in result[platform]:
                f.write(f"### {p['id']}\n\n{p['text']}\n\n---\n\n")

    total = sum(len(result[p]) for p in ("x", "bluesky", "linkedin"))
    print(f"\nwrote {os.path.relpath(OUT_JSON, HERE)} and {os.path.relpath(OUT_MD, HERE)}")
    print(f"total posts: {total} (x: {len(result['x'])}, bluesky: {len(result['bluesky'])}, linkedin: {len(result['linkedin'])})")
    if not ok:
        print("WARNING: some checks failed or counts short, review above")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
