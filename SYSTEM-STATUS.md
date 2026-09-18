# Ape AI — Social Media Machine Status (2026-09-17)

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

### 4. X / Twitter — PAUSED (boss decision)
- Poster built and authed: `poster-and-scheduler/x/poster_x.py` (as @blitztheape)
- Blocked on X API credits (402 Payment Required). **Boss chose Postiz instead.**
- If Postiz handles X: leave our auth alone, just don't double-post here AND there.

### 5. LinkedIn
- Browser automation in `poster-and-scheduler/linkedin-browser/`, API stub in `linkedin-api/`
- Nothing scheduled. Postiz may replace this too.

## IF THE BOSS ADDS POSTIZ — READ THIS
Postiz is a hosted self-serve scheduler (like Buffer). It can post to IG, X, Bluesky, LinkedIn, etc.
- **Risk: DOUBLE-POSTING.** If Postiz posts to Instagram while our launchd queue also posts → duplicate content, account flags.
- **Rule: one owner per platform.** Either Postiz OR our scripts, never both, per account.
- **Safest split:** Postiz takes X + LinkedIn (the ones we haven't automated). We keep IG + YT (already live and proven).
- Our IG queue is independent of Postiz — if boss wants Postiz on IG instead, clear `schedule_queue.json` first: set all entries `"posted": true` (or empty the file to `[]`).

## KNOWN DEBTS (fix eventually)
1. **rclone shared client_id retirement** — gdrive1 uses rclone's shared Google client, being retired during 2026. Need own Google Cloud client_id before then. All Drive-hosted IG videos depend on this.
2. **Drive `uc?export=download` links are unofficial** — works (3/3 IG tests), but if IG fetches start failing, check here first.
3. **X image posts** not wired (needs OAuth 1.0a) — text-only until needed.
4. **TikTok poster** exists (`ai-video-posters/tiktok/`) but needs app audit for public posts.
5. **Uninstall stale auth launchd jobs** when sure: `com.apeai.xauth`, `com.apeai.ytauth` (one-time tools, now inert).

## FILE MAP
- `~/Desktop/ai-video-posters/` — Instagram machine (faceless reel account)
- `~/Desktop/poster-and-scheduler/` — LinkedIn, X, Bluesky, YouTube + brand voice + guardrails
- `~/Desktop/poster-and-scheduler/youtube/yt_caption_bank.json` — YT captions
- `~/Desktop/poster-and-scheduler/x-bluesky/` — Bluesky scheduler (Node)
- Drive: `gdrive1:blitz-videos/` (83 videos) · source folders untouched: `~/ape-gtm/ugc/blitz/finished/`, `~/Desktop/Blitz videos/`

## ⏰ REMINDER — OCT 1, 2026: MAKE THIS REPO PRIVATE AGAIN

This repo went PUBLIC on 2026-09-18 only to dodge the exhausted GitHub free-minute
quota (public repos = unlimited minutes). On Oct 1 the private 2,000 minutes reset.
Run: gh repo edit mrfentmen/ape-social-machine --visibility private --accept-visibility-change-consequences
Boss approved the public exposure of drafts as a stopgap. No secrets are in git.
