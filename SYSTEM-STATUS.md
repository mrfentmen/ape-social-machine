# Ape AI — Social Media Machine Status (2026-09-18)

## PLATFORM LIMITS + OUR CADENCE (locked Sep 18 evening)
Rule: posts are ALWAYS spaced 15+ min apart inside any day. Never burst.

| Platform | Hard cap (24h) | Our cadence | Notes |
|---|---|---|---|
| Threads | 250 API posts | 60/day (bumped Sep 18) | 500 char max (sweet spot 200-450); ONE topic tag per post; if body mentions AskApe, tag = #AskApe, else rotate #Investing/#AI/#Stocks/#Trading |
| Instagram | 100/day standalone API (boss's Meta Business Suite key); Postiz path also available | 20/day | reels via cloud; rate-limit block resets on rolling window |
| Bluesky | ~1,666 posts/day (3 pts/post, 5k pts/h, 35k/day); 300 logins/day | 60/day (bumped Sep 18) | no real ceiling; loop runner logs in ~1x/hour, fine |
| X (via Postiz) | no public per-account cap (old platform cap 2,400/day) | 60/day (bumped Sep 18) | Postiz publishes on its own clock |
| YouTube | ~6-10 uploads/day (API quota) | 3/day native scheduler | Codex owns video uploads |
| LinkedIn | no official cap; sane = 25/day max | 0 (200 drafts waiting) | boss's own posting method; drafts ready |

Char limits: X 280 - Bluesky 300 - Threads 500 - LinkedIn 3,000.
Cadence bumped 40 to 60/day on Threads/Bluesky/X on Sep 18 (evening block
19:00-23:45 added on top of the 9:00-18:45 grid = 60 slots at 15-min spacing).

## THREADS IS LIVE (Sep 18 evening)
- Account: blitztheape on Threads, connected via Postiz (id cmu7hxfr0001jlb0yqnr49j2v,
  pinned in postiz/threads_schedule.py). Boss accounts remain off-limits.
- Bridge: postiz/threads_schedule.py (schema|test|all|now). Threads limits: 500
  chars, 250 posts/24h (own bucket, separate from IG ~50/day and from X/BSKY).
- TAG RULE (Threads only): ONE topic tag per post (Meta API takes the first valid
  tag as the topic). Rotation: 24x #AskApe (our own new topic) + discovery tags
  #Investing #AI #Stocks #Trading. Never stack multiple tags.
- Loaded: 40 posts = 1 now (Sep 18) + 9 more today 17:30-19:30 ET + 20 on Sep 19
  (9:00-13:45) + 10 on Sep 20 (9:00-11:15). All deduped vs every other platform
  (base text without tag line is the dedupe key).

## Sep 18 evening fixes (X + Bluesky only; IG out of scope)
- **Dense loop runners shipped.** GitHub scheduled runs were firing hours late
  (cron unreliable). Both bsky + ig workflows now run a ~58-min internal loop
  (bsky: 60s ticks, ig: 120s ticks, cap 5/tick) with per-tick commit +
  rebase-retry push. Proven live: 20:30 + 20:45 UTC slots fired on time.
- **Git-race hole closed.** A lost push previously dropped a posted flag
  (would have double-posted). Reconciled against live feed; loop now retries
  pushes 3x with rebase until remote has all state.
- **Queue coverage:** Bluesky armed through Sep 30 (496 total), X scheduled
  through Sep 30 via Postiz (Sep 25-30 batch of 240 all accepted, Axel only).
- **Postiz login:** expires ~10h. Renew via `postiz_mcp.py login --wait 170`
  or paste the 127.0.0.1:8765/callback URL to `paste --url` (rescue mode).

## Sep 18 missed-day incident (RESOLVED)
Nothing was ever scheduled for Sep 18 (queues started Sep 19). Fill applied:
16 posts 4-8pm ET on Bluesky (armed in repo queue, fired live, verified) and
16 on X (Postiz, Axel only, all postIds back). Cause: day-gap in batch 1
planning. Rule: every load-up must include TODAY if any posting window remains.
Postiz login expires ~10h; use postiz_mcp.py login --wait 170, or paste the
127.0.0.1:8765/callback URL to `paste --url` (rescue mode, no listener needed).

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
  **Batch 7 DONE (2026-09-19):** drafts_bulk7.json — 200 X + 200 Bluesky in
  the Axel "Blitz" Beaumont character-sheet voice (scalps, breakouts, gaps,
  gamer energy; tagline "Think fast, trade faster."). Use B7 pools for all
  future Blitz batches. Old batches 1 to 6 sound like a research ape, not
  the sheet — phase them out for X/Bluesky if the boss wants pure sheet voice.
- **Batch 8 DONE (2026-09-19):** drafts_bulk8.json — 200 X + 200 Bluesky,
  sheet voice batch 2, deduped vs everything including batch 7.
- **Batch 9 DONE (2026-09-19):** drafts_bulk9.json — 200 X + 200 Bluesky,
  "what real people are investing in" through Blitz's lens. Research-grounded
  (ApeWisdom WSB tracker, 2026-09): SPY/QQQ top mentions, AI chips (NVDA, AMD,
  MU, NBIS, CRWV), Intel comeback, Reddit/SpaceX retail darlings, 0DTE surge,
  leveraged ETFs, 24h sessions, crypto. OPENERS_B9/BODIES_B9/CLOSERS_B9 pools.
  Tickers + slang added to humanize_rules allowlist. No figures, no advice.
- **Batch 10 DONE (2026-09-19 night):** drafts_bulk10.json — 200 X + 200
  Bluesky (Blitz persona, B7+B9 pools mixed) + 200 LinkedIn (company-page
  corporate voice, plain language, no gamer talk, disclaimer + hashtags on
  all). Deduped vs everything. DRAFTS ONLY: LinkedIn/X/Bluesky nothing
  scheduled pending boss approval. YouTube: boss said Codex handles videos;
  yt_daily_batch.py exists in youtube/ (3/4/3 spread, 10am-5pm ET, cloud
  ready with drive_urls) but is NOT wired to a workflow. YT secrets set in
  repo (YT_CLIENT_ID/SECRET/REFRESH_TOKEN).
- **Queue mix (2026-09-19):** pending Bluesky queue is now a MIX: every 3rd
  slot replaced with a batch 7 sheet-voice post (78 of 240, ~13/day through
  Sep 24). Times unchanged, zero dupes, cloud verified (240 pending no-op run).
  Future queues: sheet voice dominant (batches 7/8+). Voice rule is pinned in
  BRAND-VOICE.md under 'BLITZ CHARACTER SHEET VOICE' — canonical, read it first.
- **Hashtag rules (updated 2026-09-19, per boss):** brand tag `#AskApe`
  FIRST, then AskApeAI / ApeAI / NYC / Finance / Money / XYZ + discovery
  staples, up to 5 tags/post (MAX_TAGS=5 in blitz_pools.pick_tags). Letters
  only, tag line always last after blank line.

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
