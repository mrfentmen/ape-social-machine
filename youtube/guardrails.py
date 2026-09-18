"""Content guardrails for Ape AI social posts (Python port of x-bluesky guardrails.js).
Enforces BRAND-VOICE.md: banned cliches + forbidden financial claims.
Every post must pass validate_text() / assert_safe() before going live."""

BANNED_PHRASES = [
    # cliches
    "game changer",
    "game-changer",
    "revolutionary",
    "in today's fast-paced world",
    "delve into",
    "tapestry",
    "elevate your",
    "supercharge",
    "10x your",
    "hack the market",
    # unsafe financial claims
    "guaranteed returns",
    "guaranteed profit",
    "guaranteed signals",
    "returns guaranteed",
    "profits guaranteed",
    "guaranteed win",
    "guaranteed way to",
    "guaranteed money",
    "can't lose",
    "cant lose",
    "risk-free",
    "risk free",
    "no risk",
    "act now",
    "limited time",
    "insider tip",
    "insider info",
    "get rich",
    "sure thing",
    "always goes up",
    "never lose",
]

FORBIDDEN_CLAIM_FRAGMENTS = [
    "we guarantee",
    "guarantee you",
    "guarantees you",
    "ape ai executes trades automatically",
    "ape ai executes your trades",
    "ape ai trades for you",
    "ape ai guarantees",
    "ape ai will make you",
    "ape ai manages your money",
    "ape ai holds your money",
    "ape ai is a broker",
    "ape ai invests for you",
    "invest with ape ai and",
]


def validate_text(text):
    """Return {ok: bool, hits: list[str]} — ok is False if any banned phrase found.
    Context-aware: denials like 'no guaranteed signals' or 'we do NOT guarantee
    returns' are allowed (they REJECT the claim rather than make it)."""
    lower = (text or "").lower()
    hits = []
    for p in BANNED_PHRASES:
        if p not in lower:
            continue
        # find the banned phrase and check if it's preceded by a denial nearby
        start = 0
        safe_hit = False
        while True:
            idx = lower.find(p, start)
            if idx == -1:
                if not safe_hit:
                    hits.append(p)
                break
            window = lower[max(0, idx - 40):idx]
            if any(d in window for d in ("no ", "not ", "never ", "without ", "we do not", "don't", "dont")):
                safe_hit = True  # denial context — allowed
            start = idx + 1
    hits += [f for f in FORBIDDEN_CLAIM_FRAGMENTS if f in lower]
    return {"ok": len(hits) == 0, "hits": hits}


def assert_safe(text):
    """Raise ValueError if text violates guardrails; return text otherwise."""
    result = validate_text(text)
    if not result["ok"]:
        raise ValueError(
            "Guardrail violation: post contains banned phrase(s): " + ", ".join(result["hits"])
        )
    return text
