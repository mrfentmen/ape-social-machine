// Persistent posting rate governor.
//
// Why this exists: the cloud workflow ticks once a minute and runs
// `scheduler.js` on every tick. Any item whose time has passed counts as due, so
// when GitHub Actions delayed a run the whole backlog fired at once. Measured on
// the live queue: 78 posts in 9.8 seconds, 12 in 5s, 10 in 0.3s. Bluesky reads
// that as a spam burst, and it is the same failure mode that got the Threads
// page timed out.
//
// A per-process sleep cannot fix it, because the workflow re-invokes the script
// every minute: the sleep would end, the next tick would start, and the burst
// would continue. The limit has to survive across invocations.
//
// So the rate is measured against the queue itself. `posted_at` is written for
// every post and the workflow commits the queue back to main after each tick, so
// the newest `posted_at` is durable shared state. Reading it gives a real
// "how long since we last posted" no matter how often the script is restarted.
//
// Pure functions only (no I/O, no clock reads) so the whole rule is unit
// testable with a fixed `now`.

/** Parse a timestamp into epoch ms, or null when it is missing/unparseable. */
export function parseTime(value) {
  if (!value) return null;
  const t = Date.parse(value);
  return Number.isNaN(t) ? null : t;
}

/** Epoch ms of the newest `posted_at` in the queue, or null if never posted. */
export function lastPostedAt(queue) {
  let newest = null;
  for (const item of queue || []) {
    if (!item) continue;
    const t = parseTime(item.posted_at);
    if (t !== null && (newest === null || t > newest)) newest = t;
  }
  return newest;
}

/**
 * Decide whether a run may post at all.
 *
 * `minGapSec` is the floor between two posts on the account. When the last post
 * is closer than that, the run posts nothing and says how long is left, so the
 * backlog drains at the account's cadence instead of all at once.
 *
 * Returns { allowed, sinceSec, waitSec, lastIso }.
 */
export function governorVerdict(queue, { now, minGapSec }) {
  const last = lastPostedAt(queue);
  if (!minGapSec || minGapSec <= 0 || last === null) {
    return { allowed: true, sinceSec: null, waitSec: 0, lastIso: null };
  }
  const sinceSec = (now - last) / 1000;
  const waitSec = minGapSec - sinceSec;
  return {
    allowed: waitSec <= 0,
    sinceSec,
    waitSec: waitSec > 0 ? waitSec : 0,
    lastIso: new Date(last).toISOString(),
  };
}

/** How many seconds late an item is right now (0 when it is not yet due). */
export function overdueSeconds(item, now) {
  const due = parseTime(item && item.at);
  if (due === null) return 0;
  const late = (now - due) / 1000;
  return late > 0 ? late : 0;
}

/**
 * Split a pending item into "post it" or "too stale to post".
 *
 * A post that is hours late reads as a bot emptying a queue, and leaving it
 * pending forever backs the queue up permanently: at a 15 minute cadence a gap
 * of an hour can never be made up, because new posts keep arriving at the same
 * rate the old ones drain. `maxAgeSec` bounds that. 0 disables the rule.
 *
 * Returns { stale, lateSec }.
 */
export function staleness(item, { now, maxAgeSec }) {
  const lateSec = overdueSeconds(item, now);
  if (!maxAgeSec || maxAgeSec <= 0) return { stale: false, lateSec };
  return { stale: lateSec > maxAgeSec, lateSec };
}
