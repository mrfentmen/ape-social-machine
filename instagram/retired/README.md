# Instagram queue — RETIRED 2026-09-22

The direct-API Instagram poster that used this queue is retired. **Instagram is
now owned by Postiz.** Do not re-enable the local launchd job or the
`ig-scheduler` GitHub workflow without reading the bottom of this file.

## Why

Every Instagram API call from this app is blocked by Meta, at the **app** level,
not the token. Read-only calls fail too, and the app itself will not validate:

```
GET /me?fields=id,username,account_type          -> 400 OAuthException code 200
GET /refresh_access_token                        -> 400 OAuthException code 200
GET /v21.0/<app id>?fields=name (app access tok) -> 400 code 190 "Error validating application"
```

- App ID `2056380568328230`, account `blitztheape` (IG user `17841434263231804`).
- A refresh cannot fix it. It needs Meta Developer Support; see
  `../../../ig_api_block_support_ticket.md` (trace ids in it expire, so it must be
  sent soon after it is written).
- Of the 720 pending entries, **146 recorded that exact block** and the other 574
  were never attempted, because every runner was switched off on Sep 20.

Instagram still posts. It goes out through Postiz on integration
`cmu7hxzef04wzmo0ytstnzc6n` ("Axel Beaumont" / instagram-standalone). So the
content is being published; only this direct path is dead.

## What is here

| file | what it is |
|---|---|
| `schedule_queue.retired-2026-09-22.json` | the **complete** 725-entry queue, byte-identical (md5 `b8e40cd981271e9c8ad15c4bbdde2307`) |

It is kept for two reasons: the 720 captions and their video assignments are only
recorded here, and it is the honest record of what was scheduled.

## What the live queue now holds

`instagram/schedule_queue.json` was reduced to the **5 entries that genuinely
posted**, so their videos and captions stay out of the reuse pool:

```
2026-09-17T20:05Z  blitz-53.mp4
2026-09-18T08:00Z  blitz-10.mp4
2026-09-18T14:15Z  blitz-11.mp4
2026-09-18T14:30Z  blitz-12.mp4
2026-09-18T14:45Z  blitz-13.mp4
```

It holds posted rows only, so:

- the GitHub workflow's due-count is 0 — it no-ops and cannot fire anything
- `ig_scheduler.py run` finds nothing due
- `build_day_queue.py` still sees the 5 real posts and will not reuse them

**The 79 videos that never posted are now reusable** (84 distinct videos in the
archive, 5 of them posted), which is correct: they were never published. Their
captions return to the bank too.

## If you revive it

1. Get the Meta app unblocked first. Nothing else matters until that works.
2. **Rebuild, do not restore.** Reconstruct the schedule rather than dropping the
   archive back in, or you re-queue 720 posts dated in the past:

   ```
   cd instagram
   python3 build_day_queue.py --posts 45 --date YYYY-MM-DD --account blitztheape
   ```

3. **One owner at a time.** `instagram/schedule_queue.json` is used by the
   `ig-scheduler` GitHub workflow. `../../ai-video-posters/schedule_queue.json` is
   a *separate* queue used by the `com.apeai.igscheduler` launchd job on this Mac.
   Each script resolves its queue next to itself, so enabling both means two
   runners and two schedules against one account.
4. If Postiz is still posting Instagram at that point, decide which one owns the
   account **before** enabling either. Posting both is duplicate content.
