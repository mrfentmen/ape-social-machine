#!/usr/bin/env python3
"""Generate SEO captions for @blitztheape Instagram reels.

Same shape as the other batch generators (generate_bulk_drafts*.py): pools in,
validated drafts out, preview markdown alongside. This one writes the caption
bank the IG queue builder reads.

Rules enforced on every caption before it is accepted:
- 200 to 300 words including the tag line
- exactly 5 hashtags: #AskApe, #AskApeAI plus 3 rotating discovery tags
- under Instagram's 2,200 character caption limit
- dash free, American spelling, humanize_rules clean
- no banned phrases, no invented figures, no advice, no returns language
- contains http://AskApe.com
- unique text, unique hook/context/insight combination, unique tag set

Curated (hand written) captions already in caption_bank.json are preserved and
come first in the rotation; generated ones are appended.

Usage:
    python3 generate_ig_captions.py --count 300
    python3 generate_ig_captions.py --count 300 --dry-run
    python3 generate_ig_captions.py --count 300 --no-curated
"""

import argparse
import json
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import ig_pools  # noqa: E402
from humanize_rules import validate_human  # noqa: E402

BANK_FILE = os.path.join(HERE, "instagram", "caption_bank.json")
PREVIEW_FILE = os.path.join(HERE, "caption_bank_preview.md")

WORDS_MIN = 200
WORDS_MAX = 300
CHAR_LIMIT = 2200
HASHTAGS = 5
TARGET_IDEAL_MIN = 215  # below this we add another paragraph

BANNED = [
    "game changer", "unlock", "revolutionary", "in today's fast-paced world",
    "delve", "tapestry", "elevate", "supercharge", "10x your", "hack the market",
    "guaranteed returns", "can't lose", "risk-free", "act now", "limited time",
    "guaranteed profit", "get rich", "to the moon", "financial freedom fast",
]
FIGURE_SCAN = re.compile(
    r"\$[\d,.]+|\b\d+(?:\.\d+)?\s?%|\b\d+(?:\.\d+)?\s?(?:billion|million|trillion)\b",
    re.I,
)


def norm(text):
    return " ".join(text.split()).lower()


def load_curated():
    """Hand written captions currently in the bank, kept first in the rotation."""
    if not os.path.exists(BANK_FILE):
        return []
    data = json.load(open(BANK_FILE))
    return [c for c in data.get("captions", []) if c.get("source", "curated") == "curated"]


def build_tags(rng, used_tag_sets):
    for _ in range(50):
        extra = tuple(sorted(rng.sample(ig_pools.TAG_POOL, 3)))
        if extra not in used_tag_sets:
            used_tag_sets.add(extra)
            return ig_pools.TAG_BRAND + list(extra)
    extra = tuple(sorted(rng.sample(ig_pools.TAG_POOL, 3)))
    return ig_pools.TAG_BRAND + list(extra)


def theme_triples(rng, theme):
    """Every hook/context/insight combination for a theme, shuffled once."""
    combos = [
        (hook, context, insight)
        for hook in theme["hooks"]
        for context in theme["contexts"]
        for insight in theme["insights"]
    ]
    rng.shuffle(combos)
    return combos


def compose(rng, theme, triple, used_tag_sets):
    """Assemble one caption from a fixed triple, adding extras until it fits.

    Extra paragraphs are added 0, 1 or 2 at a time until the caption lands
    inside the 200 to 300 word window, so no caption is ever padded by hand.
    """
    hook, context, insight = triple
    extras = list(theme["extras"])
    for count in (2, 1, 0):
        if count > len(extras):
            continue
        for _ in range(12):
            chosen = rng.sample(extras, count)
            parts = [hook, context, insight] + chosen
            parts.append(rng.choice(ig_pools.CTA_BLOCK))
            parts.append(
                rng.choice(ig_pools.CTA) + " " + rng.choice(ig_pools.DISCLAIMER)
            )
            tags = build_tags(rng, used_tag_sets)
            text = "\n\n".join(parts) + "\n\n" + " ".join(tags)
            words = len(text.split())
            if WORDS_MIN <= words <= WORDS_MAX and len(text) <= CHAR_LIMIT:
                return text, tags
    return None, None


def check_caption(text, tags):
    problems = []
    low = text.lower()
    for b in BANNED:
        if b in low:
            problems.append(f"banned phrase {b!r}")
    if "http://askape.com" not in low:
        problems.append("missing http://AskApe.com")
    m = FIGURE_SCAN.search(text)
    if m:
        problems.append(f"possible invented figure {m.group()!r}")
    if len(tags) != HASHTAGS:
        problems.append(f"{len(tags)} hashtags, need exactly {HASHTAGS}")
    if len(set(tags)) != len(tags):
        problems.append("duplicate hashtag")
    if not tags[0] == ig_pools.TAG_BRAND[0] or not tags[1] == ig_pools.TAG_BRAND[1]:
        problems.append("brand tags must lead")
    words = len(text.split())
    if not WORDS_MIN <= words <= WORDS_MAX:
        problems.append(f"{words} words, need {WORDS_MIN}-{WORDS_MAX}")
    if len(text) > CHAR_LIMIT:
        problems.append(f"{len(text)} chars over {CHAR_LIMIT}")
    for ch in "-" + "\u2014\u2013\u2012\u2015\u2212":
        if ch in text:
            problems.append("dash character present")
            break
    h = validate_human(text)
    if not h["ok"]:
        problems.append("humanize: " + "; ".join(h["hits"][:3]))
    return problems


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--count", type=int, default=300, help="generated captions to add")
    p.add_argument("--seed", type=int, default=20260918)
    p.add_argument("--dry-run", action="store_true",
                   help="validate and report without writing the bank")
    p.add_argument("--no-curated", action="store_true",
                   help="drop the hand written captions and keep only generated ones")
    args = p.parse_args()

    rng = random.Random(args.seed)
    curated = [] if args.no_curated else load_curated()

    used_texts = {norm(c["text"]) for c in curated}
    used_tag_sets = set()

    # Keep the curated tag sets distinct from the generated ones.
    for c in curated:
        tags = re.findall(r"#\w+", c["text"])
        if len(tags) == HASHTAGS:
            used_tag_sets.add(tuple(sorted(tags[2:])))

    # Walk each theme's combinations in shuffled order until the count is met.
    queues = [(t, theme_triples(rng, t)) for t in ig_pools.THEMES]
    generated = []
    rejected = []
    cursor = 0
    while len(generated) < args.count:
        theme, combos = queues[cursor % len(queues)]
        cursor += 1
        if not combos:
            if all(not c for _, c in queues):
                print("combinations exhausted; lower --count or add pool lines")
                break
            continue
        triple = combos.pop()
        text, tags = compose(rng, theme, triple, used_tag_sets)
        if text is None:
            rejected.append((theme["name"], ["no block combination landed in the word window"]))
            continue
        if norm(text) in used_texts:
            continue
        problems = check_caption(text, tags)
        if problems:
            rejected.append((theme["name"], problems))
            continue
        used_texts.add(norm(text))
        generated.append({
            "title": f"{theme['name']}: {text.split('.')[0][:46].strip()}",
            "focus": theme["focus"],
            "source": "generated",
            "text": text,
        })

    bank = curated + generated
    print(f"curated kept: {len(curated)}")
    print(f"generated:    {len(generated)}")
    print(f"total bank:   {len(bank)}")
    if rejected:
        print(f"rejected:     {len(rejected)} (first 5 shown)")
        seen = set()
        for theme_name, probs in rejected[:5]:
            print(f"  {theme_name}: {probs}")

    problems = []
    seen_text = {}
    for i, c in enumerate(bank):
        text = c["text"]
        tags = re.findall(r"#\w+", text)
        problems += [f"{i}: {p}" for p in check_caption(text, tags)]
        key = norm(text)
        if key in seen_text:
            problems.append(f"{i}: duplicate text of caption {seen_text[key]}")
        seen_text[key] = i
    print(f"bank validation problems: {len(problems)}")
    for p_ in problems[:10]:
        print("  ", p_)

    if problems:
        print("NOT written: fix the problems above first.")
        return 1

    if args.dry_run:
        print("dry run: bank not written")
        return 0

    data = {
        "rotation_note": (
            f"One time use: give each post its own caption before reusing any "
            f"caption in the bank. build_day_queue.py assigns them in order and "
            f"only recycles the oldest caption once all {len(bank)} have been used. "
            f"Each caption is {WORDS_MIN}-{WORDS_MAX} words with exactly {HASHTAGS} hashtags: "
            "#AskApe + #AskApeAI always, plus 3 rotating discovery tags. "
            "Do not add or remove tags per post."
        ),
        "rules": {
            "words_min": WORDS_MIN,
            "words_max": WORDS_MAX,
            "hashtags": HASHTAGS,
            "char_limit": CHAR_LIMIT,
            "disclaimer": "Every caption ends with an educational-purposes line. Never promise returns, never call it advice.",
            "source": "curated + generate_ig_captions.py (pools in ig_pools.py)",
        },
        "captions": bank,
    }
    with open(BANK_FILE, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

    with open(PREVIEW_FILE, "w") as f:
        f.write(f"# IG caption bank preview ({len(bank)} captions)\n\n")
        f.write(f"Words {WORDS_MIN}-{WORDS_MAX}, exactly {HASHTAGS} hashtags each.\n\n")
        for i, c in enumerate(bank):
            f.write(f"## {i}. {c['title']}\n\n")
            if c.get("focus"):
                f.write(f"Focus: {c['focus']}\n\n")
            f.write(c["text"] + "\n\n")

    print(f"wrote {os.path.relpath(BANK_FILE, HERE)} and {os.path.relpath(PREVIEW_FILE, HERE)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
