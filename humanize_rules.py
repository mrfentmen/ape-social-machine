"""Humanized-text rules for Ape AI social posts. Enforces BRAND-VOICE.md
'Humanized Text Rules': no dashes of any kind, clean punctuation spacing,
no repeated words, no misspellings (dictionary + allowlist + stemmer).

validate_human() returns {ok: bool, hits: [str]} for any post text.
Every batch generator must run this on every post before output.
"""

import os
import re

# ---------------------------------------------------------------- allowlist
# Words the 1934-era system dictionary lacks or would flag. Finance, tech, brand, modern usage.
ALLOW = {
    "ape", "apes", "askape", "nvda", "eps", "kpi", "kpis", "roi", "etf", "etfs",
    "ipo", "sec", "cfa", "yoy", "qoq", "mom", "ytd", "cagr", "ebitda",
    "fintech", "fintechs", "app", "apps", "ai", "api", "apis",
    "buybacks", "buyback", "capex", "opex", "fintwit",
    "website", "websites", "ok", "okay",
    "backtest", "backtests",
    "vibe", "vibes",
    "hype", "hypey",
    "tab", "tabs",
    "com",  # AskApe.com after punctuation splitting
    "bs",
    # Brand + persona words (Axel "Blitz" Beaumont character sheet, 2026-09-19)
    "askapeai", "apeai", "nyc", "xyz", "hodl", "hodling", "bro", "bros",
    "tp", "sl", "bag", "bags", "degen", "degens", "scalp", "scalper",
    "scalping", "scalped", "snipe", "sniped", "sniping", "rekt", "fomo",
    "yeet", "gainz", "bagholder", "bagholders", "unhinged", "coiled",
    "twitchy", "twitch", "twitches", "flashy", "snappy", "premarket",
    "afterhours", "tape", "gibbon", "gibbons", "sniper", "snipers",
}

# ---------------------------------------------------------------- dictionary
_DICT_PATHS = ("/usr/share/dict/words", "/usr/share/dict/web2")


CONTRACTIONS = {
    "don't", "doesn't", "isn't", "it's", "that's", "can't", "won't", "wasn't",
    "aren't", "hasn't", "haven't", "didn't", "you're", "they're", "there's",
    "what's", "we're", "we've", "let's", "someone's", "nobody's", "everyone's",
    "anyone's", "you've", "you'll", "we'll", "i've", "i'll", "i'm", "i'd",
    "weren't", "shouldn't", "couldn't", "wouldn't", "hadn't", "mustn't",
    "isn", "don", "doesn", "didn", "wasn", "aren", "hasn", "haven", "won",
    "weren", "shouldn", "couldn", "wouldn",
}

WORDLIKE = {"box", "near", "nap"}

# Correct English forms missing from the 1934-era web2 dictionary (verified one by one).
COMMON = {
    "has", "using", "paid", "held", "aspirational", "closest", "healthiest",
    "flashier", "scariest", "decoding", "hardest", "anymore", "deciding",
    "baseline", "fastest", "cheapest", "skimmed", "copies", "loudest",
    "advertised", "executing", "describing", "surprised", "underrated",
    "averaging", "updated", "itemized", "humbling", "wiped", "knives",
    "confusing", "smartest", "challenging", "checklists", "smarter",
    "planned", "teenager", "slower", "solved", "workflows", "unstructured",
    "companies", "qualifies", "summaries", "tagging", "closing", "shortcuts",
    "monetizing", "survived", "sourced", "replacing", "skipped", "optimized",
    "gatekeeping", "rebalances", "readiness", "unsafe", "recurring",
    "resilient", "attention", "rotation", "offering", "sophisticated",
    "tv", "info", "google", "googled", "youtube",
}


def _load_dict():
    for p in _DICT_PATHS:
        if os.path.exists(p):
            with open(p, errors="ignore") as f:
                words = {w.strip().lower() for w in f if w.strip()}
            return words
    raise SystemExit("no system dictionary found; cannot spellcheck")


_WORDS = _load_dict()
_DICT_SET = _WORDS | ALLOW

_PUNCT = re.compile(r"[^a-z'\s]")
_TOKEN = re.compile(r"[a-z']+")


def _known(w: str) -> bool:
    return w in _DICT_SET or w in CONTRACTIONS or w in WORDLIKE or w in COMMON


def _known_stem(w: str) -> bool:
    """Aggressive stemmer: strips suffixes and checks the core against dict+allow."""
    if _known(w):
        return True
    # possessive already stripped upstream; contraction parts checked upstream
    suffixes = (
        ("iest", 4, "y"), ("ier", 3, "y"),
        ("ies", 3, "y"), ("ves", 3, "f"),
        ("es", 2, ""), ("s", 1, ""),
        ("ing", 3, ""), ("ing", 3, "e"),
        ("ed", 2, ""), ("ed", 2, "e"),
        ("er", 2, ""), ("est", 3, ""), ("ly", 2, ""),
        ("ation", 5, "e"), ("ation", 5, ""),
        ("ment", 4, ""), ("ness", 4, ""), ("able", 4, ""), ("ible", 4, ""),
        ("ive", 3, "e"), ("ive", 3, ""), ("ous", 3, ""), ("ful", 3, ""),
        ("ish", 3, ""), ("less", 4, ""),
    )
    for suf, cut, add in suffixes:
        if w.endswith(suf) and len(w) - cut >= 2:
            base = w[:-cut]
            # variant stems: with add, with silent e, and bare
            for stem in (base + add, base + "e", base):
                if _known(stem):
                    return True
            # doubled consonant: planned -> plan(ned), humbling -> hum(b)ling
            if len(base) >= 4 and base[-1] == base[-2] and _known(base[:-1]):
                return True
    # prefixes: un-, re-, over-, under-, out-, pre-, mis-, non-
    for pre in ("un", "re", "over", "under", "out", "pre", "mis", "non", "anti"):
        if w.startswith(pre) and len(w) > len(pre) + 2 and _known_stem(w[len(pre):]):
            return True
    # compounds joined without space: check tail words of len>=3
    for i in range(3, len(w) - 2):
        head, tail = w[:i], w[i:]
        if _known(head) and _known_stem(tail):
            return True
    return False


def _words_ok(text: str) -> list:
    """Words the dictionary does not know and the allowlist does not cover."""
    bad = []
    stripped = _PUNCT.sub(" ", text.lower())
    for w in _TOKEN.findall(stripped):
        w = w.strip("'")
        if not w:
            continue
        if _known(w):
            continue
        # possessives: market's -> market, investing's -> investing (then stem)
        if w.endswith("'s") and (_known(w[:-2]) or _known_stem(w[:-2])):
            continue
        # contractions: you've -> you + 've
        if "'" in w:
            parts = [p for p in w.split("'") if p]
            if all(_known(p) or p in ("ve", "ll", "re", "s", "t", "d", "m") for p in parts):
                continue
        if _known_stem(w):
            continue
        bad.append(w)
    return bad


# ---------------------------------------------------------------- checks
DASH_CHARS = "\u2014\u2013\u2012\u2015\u2212-"  # em, en, figure, horizontal bar, minus, hyphen


def validate_human(text: str) -> dict:
    """Return {ok, hits} per BRAND-VOICE.md humanized rules."""
    hits = []
    if not text:
        return {"ok": True, "hits": hits}

    # 1. any dash character anywhere
    for ch in set(DASH_CHARS):
        if ch in text:
            hits.append(f"dash character {ch!r} found; rewrite without dashes")

    # 2. punctuation spacing: space before ,.;:?!  and double spaces
    if re.search(r"\s+[,.;:?!]", text):
        hits.append("space before punctuation")
    if re.search(r"\S\s{2,}\S", text.replace("\n\n", "|").replace("\n", "|")):
        hits.append("double space inside text")
    # quote style: straight only
    if "\u201c" in text or "\u201d" in text:
        hits.append("curly double quotes; use straight quotes")
    if "\u2018" in text or "\u2019" in text:
        hits.append("curly single quotes/apostrophes; use straight apostrophes")

    # 3. repeated words in a row ("the the")
    for m in re.finditer(r"\b(\w+)\s+\1\b", text, re.I):
        hits.append(f"repeated word: {m.group(0)!r}")

    # 4. spelling
    bad = _words_ok(text)
    if bad:
        hits.append("unknown words: " + ", ".join(sorted(set(bad))[:8]))

    # 5. spelled-out numbers that should be digits (common ones; small ones ok)
    for w in ("eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
              "seventeen", "eighteen", "nineteen", "twenty", "thirty", "forty",
              "fifty", "sixty", "seventy", "eighty", "ninety", "hundred",
              "thousand", "million", "billion"):
        if re.search(rf"\b{w}\b", text, re.I):
            hits.append(f"spelled-out number '{w}'; use digits or rephrase")

    return {"ok": len(hits) == 0, "hits": hits}


def assert_human(text: str) -> str:
    r = validate_human(text)
    if not r["ok"]:
        raise ValueError("Humanize violation: " + "; ".join(r["hits"]))
    return text


if __name__ == "__main__":
    tests = [
        ("Research first. Conviction after.", True),
        ("A portfolio's record doesn't lie. It can't.", True),
        ("The hardest part of investing was never access. It's translation.", True),
        ("Most people haven't decided what they're avoiding.", True),
        ("A fast paced market is often a co-ordinated one \u2014 believe it.", False),
        ("I read the 10K , then decided.", False),
        ("eleven tools for investors", False),
        ("guidance cuts get one line and then people act surprised", True),
        ("backtests don't pay for groceries", True),
        ("the market can stay irrational. humbling on both ends", True),
        ("one time charge appears in a lot of companies", True),
        ("analyst upgrades cluster near highs", True),
        ("a smart teenager would get it", True),
        ("checklists make you consistent", True),
        ("the loudest person's homework", True),
        ("executing on the plan", True),
        ("mostly boring infrastructure", True),
    ]
    fails = 0
    for text, expect_ok in tests:
        r = validate_human(text)
        got_ok = r["ok"]
        if got_ok != expect_ok:
            fails += 1
            print(f"WRONG (expected {'OK' if expect_ok else 'FAIL'}): {text!r} -> {r['hits']}")
    print(f"{len(tests) - fails}/{len(tests)} tests passed")
