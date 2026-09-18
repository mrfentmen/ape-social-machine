"""Batch 4 generator: voice split edition.

X (@blitztheape) + Bluesky (axelblitzbeaumont.bsky.social): BLITZ VOICE.
    First person ape persona, punchy, irreverent. Pools: blitz_pools.py
LinkedIn (Ape AI company page): SKILL VOICE per skill.txt.
    Intelligent, discussion driven, framework based. Pools: skill_li_pools.py

200 per platform (600 total). All rules enforced on every post:
guardrails, banned phrases, humanized text (zero dashes, spellchecked),
char limits, no invented figures. Cross-batch dedupe vs ALL prior files
(drafts_x_linkedin.json, drafts_bulk.json, 2, 3), within batch, and
across X and Bluesky (they share the same key space so no post repeats
between the two accounts).

Drafts only. Nothing scheduled, nothing posted.

Usage:
    python3 generate_bulk_drafts4.py            # generate + verify
    python3 generate_bulk_drafts4.py --verify   # re-run checks only
"""

import json
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_JSON = os.path.join(HERE, "drafts_bulk4.json")
OUT_MD = os.path.join(HERE, "drafts_bulk4_preview.md")

sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "youtube"))
import blitz_pools  # noqa: E402
import skill_li_pools  # noqa: E402
from humanize_rules import validate_human  # noqa: E402
from guardrails import validate_text  # noqa: E402

BANNED = ["game changer", "unlock", "revolutionary", "fast-paced", "delve",
          "tapestry", "elevate", "supercharge", "10x your", "hack the market",
          "guaranteed returns", "can't lose", "risk-free", "act now", "limited time"]

LIMITS = {"x": 280, "bluesky": 300, "linkedin": 3000}
TARGETS = {"x": 200, "bluesky": 200, "linkedin": 200}
DISCLAIMER = "Educational purposes only. Not financial advice."

PREV_FILES = ("drafts_x_linkedin.json", "drafts_bulk.json",
              "drafts_bulk2.json", "drafts_bulk3.json")


def norm(text: str) -> str:
    return " ".join(text.split()).lower()


def load_previous_texts() -> set:
    old = set()
    for name in PREV_FILES:
        path = os.path.join(HERE, name)
        if not os.path.exists(path):
            continue
        with open(path) as f:
            data = json.load(f)
        for plat in ("x", "bluesky", "linkedin"):
            for p in data.get(plat, []):
                old.add(norm(p["text"]))
    return old


def gen_blitz(platform: str, count: int, taken: set) -> list:
    """X/Bluesky Blitz voice: opener+body | body+closer | opener+body+closer."""
    r = random.Random(f"bulk4-{platform}")
    limit = LIMITS[platform]
    out, attempts = [], 0
    while len(out) < count and attempts < 1_000_000:
        attempts += 1
        style = r.random()
        if style < 0.35:
            parts = [r.choice(blitz_pools.OPENERS), r.choice(blitz_pools.BODIES)]
        elif style < 0.70:
            parts = [r.choice(blitz_pools.BODIES), r.choice(blitz_pools.CLOSERS)]
        else:
            parts = [r.choice(blitz_pools.OPENERS), r.choice(blitz_pools.BODIES),
                     r.choice(blitz_pools.CLOSERS)]
        text = "\n\n".join(parts)
        if len(text) > limit:
            continue
        key = norm(text)
        if key in taken:
            continue
        taken.add(key)
        out.append({"id": f"{platform}{len(out) + 1}", "text": text})
    if len(out) < count:
        raise SystemExit(f"pool exhausted for {platform}: only {len(out)}/{count}")
    return out


def gen_skill_li(count: int, taken: set) -> list:
    """LinkedIn skill voice: hook + mid + body + CTA + disclaimer."""
    r = random.Random("bulk4-linkedin")
    out, attempts = [], 0
    while len(out) < count and attempts < 1_000_000:
        attempts += 1
        text = (
            f"{r.choice(skill_li_pools.OPENERS)}\n\n"
            f"{r.choice(skill_li_pools.MID)} {r.choice(skill_li_pools.BODIES)}\n\n"
            f"{r.choice(skill_li_pools.CTAS)}\n\n"
            f"{DISCLAIMER}"
        )
        if len(text) > LIMITS["linkedin"]:
            continue
        key = norm(text)
        if key in taken:
            continue
        taken.add(key)
        out.append({"id": f"li{len(out) + 1}", "text": text})
    if len(out) < count:
        raise SystemExit(f"pool exhausted for linkedin: only {len(out)}/{count}")
    return out


def check(posts: list, platform: str) -> list:
    problems = []
    limit = LIMITS[platform]
    safe_num = re.compile(r"\b(10K|10Q|13F|401\(k\)|S1)\b|\b(19|20)\d{2}\b|[$€£]\d|\b\d{1,2}%\b|\$\d+k\b")
    for p in posts:
        t = p["text"]
        low = t.lower()
        for b in BANNED:
            if b in low:
                problems.append(f"{p['id']}: banned phrase '{b}'")
        if len(t) > limit:
            problems.append(f"{p['id']}: {len(t)} chars > {platform} limit {limit}")
        for m in re.finditer(r"\$[\d,.]+|\b\d{2,}\.\d%|\b\d+(?:\.\d+)?\s?(?:billion|million|trillion)\b", t, re.I):
            if not safe_num.search(m.group()):
                problems.append(f"{p['id']}: possible invented figure: {m.group()!r}")
        g = validate_text(t)
        if not g["ok"]:
            problems.append(f"{p['id']}: guardrails hits: {g['hits']}")
        h = validate_human(t)
        if not h["ok"]:
            problems.append(f"{p['id']}: humanize hits: {h['hits']}")
    return problems


def verify_against_old(posts: list, old_keys: set) -> list:
    return [f"{p['id']} duplicates a previous-batch post"
            for p in posts if norm(p["text"]) in old_keys]


def write_outputs(all_posts: dict):
    total = sum(len(v) for v in all_posts.values())
    with open(OUT_JSON, "w") as f:
        json.dump({
            "note": ("600 BULK DRAFTS, BATCH 4, voice split edition. "
                     "X posts as @blitztheape and Bluesky posts as axelblitzbeaumont.bsky.social "
                     "in BLITZ voice (first person ape persona). "
                     "LinkedIn posts as the company page (LINKEDIN_ORG_URN) in SKILL voice "
                     "per the original skill file. Humanized: zero dashes of any kind, spellchecked. "
                     "Drafts only, nothing scheduled or posted. Deduped against all prior batches "
                     "and across X and Bluesky."),
            **all_posts,
        }, f, indent=2, ensure_ascii=False)
    print(f"wrote {OUT_JSON}")

    with open(OUT_MD, "w") as f:
        f.write(f"# Bulk Draft Preview: Batch 4 ({total} posts, voice split)\n\n")
        f.write("DRAFTS ONLY. Nothing scheduled or posted.\n")
        f.write("X + Bluesky: BLITZ voice (first person ape persona).\n")
        f.write("LinkedIn: SKILL voice (company page, discussion driven).\n")
        f.write("All posts pass: guardrails, banned phrases, char limits, humanized rules "
                "(no dashes, spellchecked). Zero overlap with prior batches and across accounts.\n")
        for platform, label in [("x", "X, Blitz voice (as @blitztheape)"),
                                ("bluesky", "Bluesky, Blitz voice (as @axelblitzbeaumont.bsky.social)"),
                                ("linkedin", "LinkedIn, Skill voice (as Ape AI company page)")]:
            f.write(f"\n***\n\n## {label}: {len(all_posts[platform])} drafts\n\n")
            for p in all_posts[platform]:
                f.write(f"### {p['id']} ({len(p['text'])} chars)\n\n{p['text']}\n\n")
    print(f"wrote {OUT_MD}")


def main():
    verify_only = "--verify" in sys.argv
    old_keys = load_previous_texts()
    print(f"loaded {len(old_keys)} previous post texts from {', '.join(PREV_FILES)}")

    if verify_only:
        with open(OUT_JSON) as f:
            saved = json.load(f)
        all_posts = {k: saved[k] for k in ("x", "bluesky", "linkedin")}
        ok = True
        # also recheck cross-platform dupes
        keys = [norm(p["text"]) for posts in all_posts.values() for p in posts]
        dupes = len(keys) - len(set(keys))
        for platform, posts in all_posts.items():
            probs = check(posts, platform)
            overlaps = verify_against_old(posts, old_keys)
            print(f"{platform}: {len(posts)} drafts | {len(probs)} problems | "
                  f"{len(overlaps)} cross-batch duplicates")
            for x in (probs + overlaps)[:10]:
                print("  -", x)
            ok = ok and not probs and not overlaps
        print(f"within batch + across platform duplicates: {dupes}")
        ok = ok and dupes == 0
        print("VERIFY:", "PASS" if ok else "FAIL")
        raise SystemExit(0 if ok else 1)

    # one shared 'taken' set: prevents X/Bluesky repeats and cross-platform dupes
    taken = set(old_keys)
    x_posts = gen_blitz("x", TARGETS["x"], taken)
    bsky_posts = gen_blitz("bluesky", TARGETS["bluesky"], taken)
    li_posts = gen_skill_li(TARGETS["linkedin"], taken)

    for p in x_posts:
        p["post_as"] = "blitztheape"
        p["voice"] = "blitz"
    for p in bsky_posts:
        p["post_as"] = "axelblitzbeaumont.bsky.social"
        p["voice"] = "blitz"
    for p in li_posts:
        p["post_as"] = "company_page"
        p["account"] = "Ape AI company page"
        p["voice"] = "skill"

    all_posts = {"x": x_posts, "bluesky": bsky_posts, "linkedin": li_posts}

    all_problems = []
    for platform, posts in all_posts.items():
        probs = check(posts, platform)
        all_problems.extend(probs)
        print(f"{platform}: {len(posts)} drafts | {len(probs)} problems")
    for prob in all_problems[:20]:
        print("  -", prob)

    overlaps = []
    for platform, posts in all_posts.items():
        overlaps.extend(verify_against_old(posts, old_keys))
    print(f"cross-batch duplicates vs all prior batches: {len(overlaps)}")
    for o in overlaps[:10]:
        print("  -", o)

    if all_problems or overlaps:
        raise SystemExit("verification failed, see above")

    write_outputs(all_posts)
    print(f"TOTAL: {sum(len(v) for v in all_posts.values())} drafts. Nothing scheduled, nothing posted.")


if __name__ == "__main__":
    main()
