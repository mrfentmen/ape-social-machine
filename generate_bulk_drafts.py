"""Bulk draft generator for Ape AI social posts — X, Bluesky, LinkedIn. (Canonical)

Voice: BRAND-VOICE.md (corporate-page tone, dry, no narrator, no invented
figures) + Humanized Text Rules (no dashes of any kind, clean punctuation,
no repeated words, no misspellings). Lines live in pools.py; enforcement in
humanize_rules.py + youtube/guardrails.py.

Cross-batch dedupe vs ALL prior draft files (hand-written + every generated
batch). Produces DRAFTS ONLY. Nothing scheduled, nothing posted.

Batch 1 (this file, canonical):  drafts_bulk.json  + drafts_bulk_preview.md
Batch 2 (thin wrapper):          drafts_bulk2.json + drafts_bulk2_preview.md
Batch 3 (thin wrapper):          drafts_bulk3.json + drafts_bulk3_preview.md

Usage:
    python3 generate_bulk_drafts.py            # canonical batch: 100 per platform
    python3 generate_bulk_drafts.py --verify   # re-run checks only
"""

import json
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_JSON = os.path.join(HERE, "drafts_bulk.json")
OUT_MD = os.path.join(HERE, "drafts_bulk_preview.md")

sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "youtube"))
import pools  # noqa: E402
from humanize_rules import validate_human  # noqa: E402
from guardrails import validate_text  # noqa: E402

BANNED = ["game changer", "unlock", "revolutionary", "fast-paced", "delve",
          "tapestry", "elevate", "supercharge", "10x your", "hack the market",
          "guaranteed returns", "can't lose", "risk-free", "act now", "limited time"]

LIMITS = pools.LIMITS
TARGETS = pools.TARGETS

CANONICAL_PREV = ("drafts_x_linkedin.json", "drafts_bulk2.json", "drafts_bulk3.json")


def norm(text: str) -> str:
    """Normalized dedupe key: collapsed whitespace, lowercase."""
    return " ".join(text.split()).lower()


def load_previous_texts(prev_files) -> set:
    old = set()
    for name in prev_files:
        path = os.path.join(HERE, name)
        if not os.path.exists(path):
            continue
        with open(path) as f:
            data = json.load(f)
        for plat in ("x", "bluesky", "linkedin"):
            for p in data.get(plat, []):
                old.add(norm(p["text"]))
    return old


def gen_shorts(platform: str, count: int, old_keys: set, seed_key: str) -> list:
    r = random.Random(seed_key)
    limit = LIMITS[platform]
    seen, out, attempts = set(), [], 0
    while len(out) < count and attempts < 500_000:
        attempts += 1
        style = r.random()
        if style < 0.35:
            parts = [r.choice(pools.OPENERS), r.choice(pools.BODIES_SHORT)]
        elif style < 0.70:
            parts = [r.choice(pools.BODIES_SHORT), r.choice(pools.CLOSERS_SHORT)]
        else:
            parts = [r.choice(pools.OPENERS), r.choice(pools.BODIES_SHORT), r.choice(pools.CLOSERS_SHORT)]
        text = "\n\n".join(parts)
        if len(text) > limit:
            continue
        key = norm(text)
        if key in seen or key in old_keys:
            continue
        seen.add(key)
        out.append({"id": f"{platform}{len(out) + 1}", "text": text})
    if len(out) < count:
        raise SystemExit(f"pool exhausted for {platform}: only {len(out)}/{count}")
    return out


def gen_linkedin(count: int, old_keys: set, seed_key: str) -> list:
    r = random.Random(seed_key)
    seen, out, attempts = set(), [], 0
    while len(out) < count and attempts < 500_000:
        attempts += 1
        text = (
            f"{r.choice(pools.OPENERS)}\n\n"
            f"{r.choice(pools.MID_CONNECTORS)} {r.choice(pools.BODIES_LONG)}\n\n"
            f"{r.choice(pools.CLOSERS_CTA)}\n\n"
            f"{pools.DISCLAIMER}"
        )
        if len(text) > LIMITS["linkedin"]:
            continue
        key = norm(text)
        if key in seen or key in old_keys:
            continue
        seen.add(key)
        out.append({"id": f"li{len(out) + 1}", "text": text})
    if len(out) < count:
        raise SystemExit(f"pool exhausted for linkedin: only {len(out)}/{count}")
    return out


def check(posts: list, platform: str) -> list:
    """All rules: banned phrases, guardrails.py, char limits, fabricated figures,
    humanized text (dashes, punctuation, spelling)."""
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


def build(prev_files, out_json, out_md, seed, seed_key, note, verify_only=False):
    """Generate one batch (or verify an existing one) against prev_files."""
    old_keys = load_previous_texts(prev_files)
    print(f"loaded {len(old_keys)} previous post texts from {', '.join(prev_files)}")

    if verify_only:
        with open(out_json) as f:
            saved = json.load(f)
        all_posts = {k: saved[k] for k in ("x", "bluesky", "linkedin")}
        ok = True
        for platform, posts in all_posts.items():
            probs = check(posts, platform)
            overlaps = verify_against_old(posts, old_keys)
            print(f"{platform}: {len(posts)} drafts | {len(probs)} problems | "
                  f"{len(overlaps)} cross-batch duplicates")
            for x in (probs + overlaps)[:10]:
                print("  -", x)
            ok = ok and not probs and not overlaps
        print("VERIFY:", "PASS" if ok else "FAIL")
        return ok

    x_posts = gen_shorts("x", TARGETS["x"], old_keys, f"{seed_key}-x")
    bsky_posts = gen_shorts("bluesky", TARGETS["bluesky"], old_keys, f"{seed_key}-bluesky")
    li_posts = gen_linkedin(TARGETS["linkedin"], old_keys, f"{seed_key}-linkedin")

    for p in x_posts:
        p["post_as"] = "blitztheape"
    for p in bsky_posts:
        p["post_as"] = "axelblitzbeaumont.bsky.social"
    for p in li_posts:
        p["post_as"] = "company_page"
        p["account"] = "Ape AI company page"

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
        raise SystemExit("verification failed — see above")

    total = sum(len(v) for v in all_posts.values())
    with open(out_json, "w") as f:
        json.dump({"note": note, **all_posts}, f, indent=2, ensure_ascii=False)
    print(f"wrote {out_json}")

    with open(out_md, "w") as f:
        f.write(f"# Bulk Draft Preview ({total} posts, humanized)\n\n")
        f.write("DRAFTS ONLY. Nothing scheduled or posted.\n")
        f.write("All text passes: guardrails, banned phrases, char limits, humanized rules "
                "(no dashes, clean punctuation, spellchecked). Zero overlap with prior batches.\n")
        for platform, label in [("x", "X (as @blitztheape)"),
                                ("bluesky", "Bluesky (as @axelblitzbeaumont.bsky.social)"),
                                ("linkedin", "LinkedIn (as Ape AI company page)")]:
            f.write(f"\n***\n\n## {label}: {len(all_posts[platform])} drafts\n\n")
            for p in all_posts[platform]:
                f.write(f"### {p['id']} ({len(p['text'])} chars)\n\n{p['text']}\n\n")
    print(f"wrote {out_md}")
    print(f"TOTAL: {total} drafts. Nothing scheduled, nothing posted.")
    return True


def main():
    verify_only = "--verify" in sys.argv
    note = ("300 BULK DRAFTS (canonical batch 1, humanized: zero dashes of any kind, "
            "spellchecked). Drafts only, nothing scheduled or posted. "
            "X posts as @blitztheape. Bluesky posts as axelblitzbeaumont.bsky.social. "
            "LinkedIn posts as the company page (LINKEDIN_ORG_URN). "
            "Voice rules: BRAND VOICE doc. Generated by generate_bulk_drafts.py; "
            "deduped against all prior batches.")
    ok = build(CANONICAL_PREV, OUT_JSON, OUT_MD, 20260920, "canonical-20260920",
               note, verify_only=verify_only)
    if verify_only:
        raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
