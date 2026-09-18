#!/usr/bin/env python3
"""Batch 10 generator: 200 X + 200 Bluesky (Blitz voice, B7+B9 pools) and
200 LinkedIn (company page voice, plain language, disclaimer, hashtags).

Rules per boss (2026-09-19 night):
- X + Bluesky: Blitz persona (character sheet voice, retail-flow pools).
- LinkedIn: corporate ape, company-page voice, NO gamer talk, plain everyday
  words so new people understand.
- Hashtags on every post in all platforms (#AskApe first, up to 5).
- Humanized rules on everything. Drafts only: NOTHING is scheduled or posted.
"""

import json
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import blitz_pools  # noqa: E402
import pools  # noqa: E402
import skill_li_pools  # noqa: E402
from humanize_rules import validate_human  # noqa: E402

OUT_JSON = os.path.join(HERE, "drafts_bulk10.json")
OUT_MD = os.path.join(HERE, "drafts_bulk10_preview.md")

LIMITS = {"x": 280, "bluesky": 300, "linkedin": 3000}
COUNTS = {"x": 200, "bluesky": 200, "linkedin": 200}
TAG_RESERVE = 50

BANNED = [
    "game changer", "unlock", "revolutionary", "in today's fast-paced world",
    "delve", "tapestry", "elevate", "supercharge", "10x your", "hack the market",
    "guaranteed returns", "can't lose", "risk-free", "act now", "limited time",
]
DISCLAIMER_SCAN = re.compile(
    r"\$[\d,.]+|\b\d{2,}\.\d%|\b\d+(?:\.\d+)?\s?(?:billion|million|trillion)\b", re.I)

DISCLAIMER = pools.DISCLAIMER  # "Educational purposes only. Not financial advice."


def norm(t):
    return " ".join(t.split()).lower()


def load_used_texts():
    """Everything already drafted or queued anywhere - never repeat."""
    used = set()
    files = ["drafts_bulk.json", "drafts_bulk2.json", "drafts_bulk3.json",
             "drafts_bulk4.json", "drafts_bulk5.json", "drafts_bulk6.json",
             "drafts_bulk7.json", "drafts_bulk8.json", "drafts_bulk9.json",
             "drafts_x_linkedin.json"]
    for fn in files:
        p = os.path.join(HERE, fn)
        if not os.path.exists(p):
            continue
        data = json.load(open(p))
        for plat in ("x", "bluesky", "linkedin"):
            for post in data.get(plat, []):
                used.add(norm(post["text"]))
    extra = [
        os.path.join(HERE, "x-bluesky", "bsky_scheduled_posts.json"),
        os.path.join(HERE, "postiz", "x_batch1_staging.json"),
        os.path.join(HERE, "postiz", "x_batch1_scheduled.json"),
        os.path.join(HERE, "postiz", "x_batch2_staging.json"),
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
        if "#AskApe" not in t:
            problems.append(f"{p['id']}: missing #AskApe")
    return problems


def blitz_text(r, used_keys):
    """One Blitz-voice body from B7 (sheet) or B9 (retail-flow) pools."""
    use9 = r.random() < 0.5
    O = blitz_pools.OPENERS_B9 if use9 else blitz_pools.OPENERS_B7
    B = blitz_pools.BODIES_B9 if use9 else blitz_pools.BODIES_B7
    C = blitz_pools.CLOSERS_B9 if use9 else blitz_pools.CLOSERS_B7
    style = r.random()
    if style < 0.30:
        parts = [r.choice(O), r.choice(B)]
    elif style < 0.60:
        parts = [r.choice(B), r.choice(C)]
    elif style < 0.85:
        parts = [r.choice(O), r.choice(B), r.choice(C)]
    else:
        parts = [r.choice(O), r.choice(B), r.choice(B)]
    return "\n\n".join(parts)


def gen_blitz(platform, used):
    limit = LIMITS[platform]
    count = COUNTS[platform]
    r = random.Random(f"bulk10-{platform}")
    out, attempts = [], 0
    while len(out) < count and attempts < 2_000_000:
        attempts += 1
        text = blitz_text(r, used)
        if len(text) > limit or len(text) > limit - TAG_RESERVE:
            continue
        k = norm(text)
        if k in used:
            continue
        rng = random.Random(f"tags-bulk10-{platform}-{attempts}")
        tags = blitz_pools.pick_tags(rng, platform, limit - len(text) - 2)
        if not tags:
            continue
        full = f"{text}\n\n{tags}"
        if not validate_human(full)["ok"]:
            continue
        used.add(k)
        out.append({"id": f"{platform}{len(out) + 1}", "text": full})
    return out


def gen_linkedin(used):
    """Company-page voice: opener + mid + body + CTA + disclaimer + tags.

    Plain language: no gamer slang, no mascot narrator. Lines come from
    skill_li_pools (pre-validated). Hashtags per boss rule (5, #AskApe first).
    """
    count = COUNTS["linkedin"]
    r = random.Random("bulk10-linkedin")
    li_tags = ["#AskApe", "#Finance", "#Investing", "#Fintech", "#AskApeAI"]
    alt_tags = ["#AskApe", "#Investing", "#NYC", "#Fintech", "#ApeAI"]
    out, attempts = [], 0
    while len(out) < count and attempts < 500_000:
        attempts += 1
        body = (
            f"{r.choice(skill_li_pools.OPENERS)}\n\n"
            f"{r.choice(skill_li_pools.MID)} {r.choice(skill_li_pools.BODIES)}\n\n"
            f"{r.choice(skill_li_pools.CTAS)}\n\n"
            f"{DISCLAIMER}"
        )
        tags = " ".join(li_tags if r.random() < 0.7 else alt_tags)
        full = f"{body}\n\n{tags}"
        if len(full) > LIMITS["linkedin"]:
            continue
        k = norm(full)
        if k in used:
            continue
        h = validate_human(full)
        if not h["ok"]:
            continue
        used.add(k)
        out.append({"id": f"li{len(out) + 1}", "text": full})
    return out


def main():
    used = load_used_texts()
    print(f"dedupe universe: {len(used)} existing texts")

    result = {"note": ("Batch 10 drafts: X + Bluesky in Blitz persona voice, "
                       "LinkedIn in company-page corporate voice (plain language). "
                       "Hashtags on all. Drafts only, nothing scheduled. "
                       "Generated 2026-09-19 night.")}
    all_ok = True
    for platform in ("x", "bluesky", "linkedin"):
        if platform == "linkedin":
            posts = gen_linkedin(used)
        else:
            posts = gen_blitz(platform, used)
        problems = check(posts, platform)
        print(f"{platform}: generated {len(posts)} posts, problems: {len(problems)}")
        for pr in problems[:5]:
            print("  !!", pr)
        if problems or len(posts) < COUNTS[platform]:
            all_ok = False
        result[platform] = posts

    with open(OUT_JSON, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    with open(OUT_MD, "w") as f:
        f.write("# Batch 10 drafts (Blitz for X/Bluesky, corporate ape for LinkedIn) - PREVIEW ONLY\n\n")
        f.write("Generated 2026-09-19 night. Hashtags on all. Drafts only: nothing scheduled.\n\n")
        for platform in ("x", "bluesky", "linkedin"):
            f.write(f"\n## {platform.upper()} ({len(result[platform])} posts)\n\n")
            for p in result[platform]:
                f.write(f"### {p['id']}\n\n{p['text']}\n\n---\n\n")

    total = sum(len(result[p]) for p in ("x", "bluesky", "linkedin"))
    print(f"\nwrote {OUT_JSON} and {OUT_MD}")
    print(f"total posts: {total} (x: {len(result['x'])}, bluesky: {len(result['bluesky'])}, linkedin: {len(result['linkedin'])})")
    if not all_ok:
        print("WARNING: some checks failed or counts short - review above")
        sys.exit(1)


if __name__ == "__main__":
    main()
