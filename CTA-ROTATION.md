# CTA Rotation Plan (2026-09-17)

How to mix CTA posts and non-CTA posts so the feeds don't feel salesy.
Applies to X (@blitztheape), Bluesky (@axelblitzbeaumont.bsky.social),
and LinkedIn (company page). Nothing here posts anything by itself.

## The inventory

| File | Posts | CTA? | Voice |
|---|---|---|---|
| drafts_bulk.json | 300 | soft (some mention AskApe.com) | corporate |
| drafts_bulk2.json | 300 | soft | corporate |
| drafts_bulk3.json | 300 | soft | corporate |
| drafts_bulk4.json | 600 | soft (~1 in 6 closers mention AskApe.com) | blitz (X/BSKY) + skill (LI) |
| drafts_bulk5.json | 120 | **hard** (every post: "Find out more at AskApe.com") | blitz + skill |
| drafts_x_linkedin.json | 10 | soft | hand-written |

Batch 5 posts are tagged `"cta": "askape"` in the JSON. Everything else is
non-CTA by default.

## The rule

**1 hard CTA per 4 posts (25% max).** Sequence pattern:

```
post 1: non-CTA (insight / observation)
post 2: non-CTA
post 3: hard CTA (from drafts_bulk5.json)
post 4: non-CTA
repeat
```

Never two hard-CTA posts in a row on the same account. Same text never
appears twice on the same account (dedupe pools already guarantee this
across all batches).

## Per-platform notes

- **X + Bluesky (Blitz):** hard CTAs work best after a strong observation
  post. Batch 5's Blitz CTAs carry the persona ("Bananas optional"), so
  they read as voice, not ads.
- **LinkedIn (company page):** skill voice CTAs are discussion-first;
  batch 5's LinkedIn posts already end with the CTA + disclaimer. Keep
  those to 1 in 4 as well, and prefer the "discussion question" posts
  from batch 4 for the other slots.

## How to draw the next posts

1. `python3 bsky_build_queue.py --days N` stages the next N days for
   Bluesky (3/day, 4h apart). It skips anything already in the sent log.
   It is STAGING ONLY. Arm with `--arm` only when the boss says go.
2. For X: hand-pick from `drafts_bulk4_preview.md` (non-CTA) and
   `drafts_bulk5_preview.md` (CTA) following the 3:1 pattern. X posting
   is manual until the API credits issue is resolved or Postiz takes over.
3. For LinkedIn: same pattern from the LinkedIn sections. Nothing posts
   until the company page connection is set up (LINKEDIN_ORG_URN).

## Guardrails that always apply

- Every post passes humanize_rules.py (zero dashes, spellchecked) and
  youtube/guardrails.py (banned phrases, unsafe claims).
- No invented figures. Ever.
- Educational disclaimer on all LinkedIn company posts.
