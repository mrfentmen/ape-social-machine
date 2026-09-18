# Ape AI — Social Media Machine Status (2026-09-18)

## LIVE-STATE SNAPSHOT (2026-09-18, session 3)

- **Hashtags: DONE.** All 1,085 X + Bluesky drafts carry `#AskApe` first + up to 2
  discovery tags (`blitz_pools.pick_tags`, patcher `add_hashtags.py`). Verified:
  1085/1085 tagged, all under limits, humanize clean.
- **Bluesky: SCHEDULING LIVE IN THE CLOUD.** Repo `ape-social-machine` runs the
  bsky-scheduler workflow every 15 min (cron `*/15 * * * *` UTC). Queue committed
  to the repo: **240 posts, Sep 19–24**, every 15 min 09:00–18:45 ET (40/day).
  Workflow posts only what's due (`scheduler.js --max-wait 60`) and commits
  posted-flags back (double-post safe). Verified no-op run Sep 18: `queue: 240
  total, 0 due, no login`. Extend with:
  `python3 bsky_build_queue.py --days 3 --start-days <offset> && python3 bsky_build_queue.py --arm`,
  then copy the queue file into the repo and push. Staging appends + dedupes
  across batches; pool has ~300 unused Bluesky drafts left after Sep 24.
- **X via Postiz: FULLY LOADED through Sep 24.** OAuth re-logged Sep 18
  (`postiz_mcp.py login`). 210 posts scheduled to **Axel Beaumont X only**
  (ID pinned below): batch 1 = 10 (Sep 19, hourly), batch 2 = 200 (Sep 20–24,
  40/day, every 15 min 09:00–18:45 ET). All tagged Blitz voice, all deduped
  against the Bluesky queue. Verified via postsListTool: target = Axel
  Beaumont on every post. Helper: `postiz/schedule_x_batch.py
  show|test|all --file <name> --chunk 40`; generic caller
  `postiz/postiz_call.py`. Postiz payload requires HTML `<p>` content,
  `attachments: []`, `isPremium`, `shortLink`, and settings
  `post_type=post`, `who_can_reply_post=everyone`. Live-post test PASSED
  Sep 18 (type:"now" -> PUBLISHED).
- **Instagram: CLOUD-OWNED since Sep 18 08:07 UTC.** launchd
  `com.apeai.igscheduler` UNLOADED (plist kept for rollback: `launchctl load
  ~/Library/LaunchAgents/com.apeai.igscheduler.plist`). Cloud workflow
  `ig-scheduler.yml` in repo `ape-social-machine` fires every 15 min, posts
  max 3/run, commits queue state back. Canary post PROVED the chain
  (media_id 17970182568152716). Queue in repo: 139 pending through Sep 24.
  Top-up ritual is now: run build_day_queue.py locally, then copy
  `~/Desktop/ai-video-posters/schedule_queue.json` into the repo and push.
  Token refresh monthly: run local `refresh_ig.py`, then re-set the
  IG_ACCESS_TOKEN secret. Videos stay on Google Drive (no Drive deletes
  from cloud; all queue items have delete_from_drive=false).
- **YouTube: 3 Shorts/day.** Sep 19 scheduled natively via --publish-at
  (blitz-58/59/60, 9am/1pm/5pm ET). Repeat daily: next videos blitz-61+,
  captions rotate from `yt_caption_bank.json`.
- **Draft pool status:** ~329 unused X drafts left (usable for Bluesky
  Sep 25+ or more X). Bluesky-voice pool is FULLY USED through Sep 24.
  Around Sep 22: run generate_bulk_drafts to make batch 6 before Sep 25,
  or Bluesky/X queues run dry.
- **Hashtag rules:** brand tag `#AskApe` mandatory first, max 3 tags/post
  (guardrails flag 5+), letters only, tag line always last after blank line.

## ⏰ REMINDER — OCT 1, 2026: MAKE ape-social-machine PRIVATE AGAIN

The repo `mrfentmen/ape-social-machine` was made PUBLIC on 2026-09-18 only because
the GitHub free-minute quota was exhausted and public repos get unlimited minutes.
**On Oct 1 the 2,000 private minutes reset -> run:**
```bash
gh repo edit mrfentmen/ape-social-machine --visibility private --accept-visibility-change-consequences
```
Then verify: `gh repo view mrfentmen/ape-social-machine --json visibility`.
Drafts are public in the meantime — that was the boss's explicit call.


Snapshot of every automated system, what runs where, and what's left.
Read this before changing anything — especially if Postiz (boss's tool) gets added.

## LIVE SYSTEMS

### 1. Instagram — @blitztheape ✅ FULLY AUTOMATED
- **What:** 20 reels/day, 4/hour bursts, 10:00–14:45 local
- **Queue:** `ai-video-posters/schedule_queue.json` — 80 pending (Sep 18–21), 1 test posted
- **Runner:** launchd `com.apeai.igscheduler` — fires every 5 min, auto
- **Captions:** `ai-video-posters/caption_bank.json` (3 Ape AI captions, rotating)
- **Videos:** hosted on Google Drive `gdrive1:blitz-videos/` (83 files), direct URLs in `drive_urls.json`
- **Token:** long-lived, refresh monthly via `instagram/refresh_ig.py`
- **Daily ritual:** `cd ~/Desktop/ai-video-posters && python3 build_day_queue.py --posts 20 --start-now`
- **Recycles videos automatically when the pool is burned (day 5+).**

### 2. YouTube — AxelBlitzBeaumont ✅ LIVE (manual trigger)
- **What:** 3 Shorts/day posted via `poster-and-scheduler/youtube/poster_youtube.py`
- **Today:** 3 live; tomorrow: 3 scheduled via native `--publish-at` (no Mac needed)
- **Captions:** `yt_caption_bank.json` (5 Shorts captions, no links)
- **Limit:** ~6 uploads/day free quota (resets midnight PT)
- **Daily ritual:** run 3 uploads (scriptable on request)
- **Auth:** OAuth token in `.env`, auto-refreshes, approved scopes verified

### 3. Bluesky ✅ EXISTS (idle)
- `poster-and-scheduler/x-bluesky/` — full poster + scheduler (Node)
- Voice rules: `BRAND-VOICE.md`
- Nothing scheduled right now. **Next: wire a daily queue like Instagram's.**

### 4. X / Twitter — Postiz owns it (boss decision) ✅ CONNECTED
- Old poster still exists (`poster-and-scheduler/x/poster_x.py`) but is superseded.
- **Postiz connection live since 2026-09-17.** Access via bridge script:
  `cd ~/Desktop/poster-and-scheduler/postiz && python3 postiz_mcp.py accounts|tools`
  (OAuth token at ~/.postiz_mcp/token.json, 0600, self-refreshing)
- **ACCOUNT MAP (from integrationList, read-only):**
  - Axel Beaumont / x → **MINE — the ONLY allowed Postiz target** (id cmu63e4kz05j5nl0y88yzl0ip)
  - askApe / x → BOSS — OFF-LIMITS (id cmqh25u0z0698o80y5z8reuf2)
  - Faizan Sattar / x → BOSS — OFF-LIMITS (id cmqel69w90187pm0ywxyimxn2)
  - Faizan Sattar / linkedin → BOSS — OFF-LIMITS (id cmqel6pc40189pm0y5vp2dc5g)
  - AskApeAI / reddit → BOSS — OFF-LIMITS (id cmqh24llw068ko80ylofxb4jn)
  - TikTok → not connected yet; slot reserved for @blitztheape when added
- Rule: every Postiz post targets Axel Beaumont's integration ID by pin, never
  by name lookup. Boss accounts are never passed to posting tools.

### 4b. TikTok — Postiz owns it (boss decision, 2026-09-17)
- **Direct TikTok API application ABANDONED.** TikTok requires a demo video of a
  fully built integration before approving an app — impossible pre-build. Boss's call.
- Nothing was deleted: credentials (client key/secret) + site verification token
  are in `poster-and-scheduler/.env` (TIKTOK_* vars) if ever revisited.
- Domain verification for askape.com was never completed (TXT record was never
  added to Cloudflare). If revisiting, that's step one.
- **Postiz will post TikTok + X.** Do not build a TikTok poster. Do not connect
  IG to Postiz (see Postiz rules below).

### 5. LinkedIn
- Browser automation in `poster-and-scheduler/linkedin-browser/`, API stub in `linkedin-api/`
- Nothing scheduled. Postiz may replace this too.

## IF THE BOSS ADDS POSTIZ — READ THIS
Postiz is a hosted self-serve scheduler (like Buffer). It can post to IG, X, Bluesky, LinkedIn, etc.
- **Risk: DOUBLE-POSTING.** If Postiz posts to Instagram while our launchd queue also posts → duplicate content, account flags.
- **Rule: one owner per platform.** Either Postiz OR our scripts, never both, per account.
- **Safest split (updated 2026-09-17):** Postiz takes X + TikTok (+ LinkedIn if
  boss uses it there). We keep IG + YT + Bluesky (already live and proven).
- If Postiz ever takes Bluesky: DISARM our runner first (empty the live queue +
  disable the workflow) before connecting it there. One owner per account, always.
- Our IG queue is independent of Postiz — if boss wants Postiz on IG instead, clear `schedule_queue.json` first: set all entries `"posted": true` (or empty the file to `[]`).

## POSTIZ — CONNECTED (2026-09-18, boss-confirmed ownership)
Bridge script: `poster-and-scheduler/postiz/postiz_mcp.py` (OAuth token at `~/.postiz_mcp/token.json`, 0600).
Connected accounts (from one read-only `integrationList` call, 2026-09-18):
- **X "Axel Beaumont"** — id `cmu63e4kz05j5nl0y88yzl0ip` → **OUR X TARGET. Pin this id in every draft.**
- X "askApe" — id `cmqh25u0z0698o80y5z8reuf2` → unassigned (boss hasn't ruled).
- X "Faizan Sattar" + LinkedIn "Faizan Sattar" — **BOSS'S PERSONAL ACCOUNTS. Never touch, never post, never disconnect.**
- Reddit "AskApeAI" — id `cmqh24llw068ko80ylofxb4jn` → unassigned (boss hasn't ruled).
- TikTok — NOT connected yet; **boss connects it himself in the Postiz UI.**
- IG / YouTube / Bluesky must NEVER be connected to Postiz (one-owner rule).
Rules: no post/schedule/draft without explicit "go" on exact content. Read-only check = `python3 postiz_mcp.py accounts`.

## KNOWN DEBTS (fix eventually)
1. **rclone shared client_id retirement** — gdrive1 uses rclone's shared Google client, being retired during 2026. Need own Google Cloud client_id before then. All Drive-hosted IG videos depend on this.
2. **Drive `uc?export=download` links are unofficial** — works (3/3 IG tests), but if IG fetches start failing, check here first.
3. **X image posts** not wired (needs OAuth 1.0a) — text-only until needed.
4. **TikTok poster** exists (`ai-video-posters/tiktok/`) but is MOOT: Postiz owns TikTok per boss decision (2026-09-17). Leave it dormant.
5. **Uninstall stale auth launchd jobs** when sure: `com.apeai.xauth`, `com.apeai.ytauth` (one-time tools, now inert).

## FILE MAP
- `~/Desktop/ai-video-posters/` — Instagram machine (faceless reel account)
- `~/Desktop/poster-and-scheduler/` — LinkedIn, X, Bluesky, YouTube + brand voice + guardrails
- `~/Desktop/poster-and-scheduler/youtube/yt_caption_bank.json` — YT captions
- `~/Desktop/poster-and-scheduler/x-bluesky/` — Bluesky scheduler (Node)
- Drive: `gdrive1:blitz-videos/` (83 videos) · source folders untouched: `~/ape-gtm/ugc/blitz/finished/`, `~/Desktop/Blitz videos/`
