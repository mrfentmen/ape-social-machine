# ape-social-machine (PRIVATE)

Ape AI (@AskApe) social posting machine. Drafts, generators, voice rules,
and the Bluesky scheduler. Private repo so the Actions free minutes apply.

## Golden rules
1. **DRAFTS ONLY until the boss says post.** Nothing scheduled or posted without an explicit go.
2. **NO SECRETS IN GIT.** All credentials live in GitHub Secrets / local .env (gitignored).
3. Voice split: X + Bluesky = BLITZ voice. LinkedIn = skill voice. See BRAND-VOICE.md.
4. Every post passes humanize_rules.py (zero dashes, spellchecked) + youtube/guardrails.py.

## Layout
- `generate_bulk_drafts*.py` — draft generators (batches 1..5, ~1,630 drafts)
- `pools.py`, `blitz_pools.py`, `skill_li_pools.py` — line pools per voice
- `humanize_rules.py`, `youtube/guardrails.py` — enforcement
- `drafts_bulk*.json` + `*_preview.md` — the drafts + human-readable previews
- `x-bluesky/` — Bluesky scheduler (Node, @atproto/api). Needs BSKY_HANDLE +
  BSKY_APP_PASSWORD (never committed; see .env.template)
- `bsky_build_queue.py` — stages Bluesky posting plans (staging only until --arm)
- `CTA-ROTATION.md` — 1 hard CTA per 4 posts plan

## Run everything from a clone
```bash
pip install nothing  # stdlib only for the python side
cd x-bluesky && npm ci   # installs the Bluesky scheduler deps
python3 generate_bulk_drafts.py --verify  # sanity check batch 1
```
