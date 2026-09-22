// Tests for the posting rate governor and the scheduler that uses it.
//
// The bug these lock down, measured on the live queue: when GitHub Actions
// delayed a run, every overdue item fired back to back — 78 posts in 9.8
// seconds, 12 in 5s, 10 in 0.3s. The governor has to hold across the cloud
// workflow's once-a-minute re-invocation, so it is driven by posted_at in the
// queue rather than by a sleep inside one process.
//
// Run: npm test        (node --test test/)

import test from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

import {
  governorVerdict,
  lastPostedAt,
  overdueSeconds,
  parseTime,
  staleness,
} from "../src/rate_governor.js";

const SCHEDULER = fileURLToPath(new URL("../src/scheduler.js", import.meta.url));
const NOW = Date.parse("2026-09-22T02:30:00Z");

test("parseTime accepts ISO and rejects junk or blanks", () => {
  assert.equal(parseTime("2026-09-22T02:00:00Z"), Date.parse("2026-09-22T02:00:00Z"));
  assert.equal(parseTime(null), null);
  assert.equal(parseTime(""), null);
  assert.equal(parseTime("not a date"), null);
});

test("lastPostedAt finds the newest posted_at, ignoring rows without one", () => {
  const queue = [
    { at: "2026-09-22T01:00:00Z", posted_at: "2026-09-22T01:00:00Z" },
    { at: "2026-09-22T02:00:00Z", posted_at: "2026-09-22T02:00:00Z" },
    { at: "2026-09-22T03:00:00Z", posted_at: null },
    null,
  ];
  assert.equal(lastPostedAt(queue), Date.parse("2026-09-22T02:00:00Z"));
  assert.equal(lastPostedAt([]), null);
  assert.equal(lastPostedAt([{ at: "x" }]), null);
});

test("governor blocks a run when the last post is closer than min-gap", () => {
  const queue = [{ posted: true, posted_at: "2026-09-22T02:25:00Z" }];
  const verdict = governorVerdict(queue, { now: NOW, minGapSec: 900 });
  assert.equal(verdict.allowed, false);
  assert.equal(verdict.sinceSec, 300);
  assert.equal(verdict.waitSec, 600);
});

test("governor allows a run once min-gap has elapsed", () => {
  const queue = [{ posted: true, posted_at: "2026-09-22T02:00:00Z" }];
  const verdict = governorVerdict(queue, { now: NOW, minGapSec: 900 });
  assert.equal(verdict.allowed, true);
  assert.equal(verdict.waitSec, 0);
});

test("governor allows a run exactly on the boundary", () => {
  const queue = [{ posted_at: "2026-09-22T02:15:00Z" }];
  assert.equal(governorVerdict(queue, { now: NOW, minGapSec: 900 }).allowed, true);
});

test("min-gap 0 disables the governor", () => {
  const queue = [{ posted_at: "2026-09-22T02:29:59Z" }];
  const verdict = governorVerdict(queue, { now: NOW, minGapSec: 0 });
  assert.equal(verdict.allowed, true);
  assert.equal(verdict.sinceSec, null);
});

test("a queue that has never posted is never blocked", () => {
  const verdict = governorVerdict([{ at: "2026-09-22T02:00:00Z" }], {
    now: NOW,
    minGapSec: 900,
  });
  assert.equal(verdict.allowed, true);
});

test("overdueSeconds counts only lateness, never negative", () => {
  // 21:00 -> 02:30 the next day is 5h30m, not 5h.
  assert.equal(overdueSeconds({ at: "2026-09-21T21:00:00Z" }, NOW), 5.5 * 3600);
  // 02:29 is one minute BEFORE the 02:30 clock, so it is 60s late, not zero.
  assert.equal(overdueSeconds({ at: "2026-09-22T02:29:00Z" }, NOW), 60);
  assert.equal(overdueSeconds({ at: "2026-09-22T02:30:00Z" }, NOW), 0);
  assert.equal(overdueSeconds({ at: "2026-09-22T03:00:00Z" }, NOW), 0);
});

test("staleness drops a post that is too late, and keeps a fresh one", () => {
  const opts = { now: NOW, maxAgeSec: 3600 };
  assert.equal(staleness({ at: "2026-09-21T21:00:00Z" }, opts).stale, true);
  assert.equal(staleness({ at: "2026-09-22T02:00:00Z" }, opts).stale, false);
});

test("maxAgeSec 0 means never stale, even for a very old post", () => {
  const opts = { now: NOW, maxAgeSec: 0 };
  assert.equal(staleness({ at: "2020-01-01T00:00:00Z" }, opts).stale, false);
});

// -- End to end, against the real script -------------------------------------
//
// These drive src/scheduler.js in a throwaway directory. The blocked case never
// reaches getAgent(), and the other case is a dry run, so no test here can post.

function runScheduler(queue, args) {
  const dir = mkdtempSync(join(tmpdir(), "bsky-gov-"));
  const file = join(dir, "bsky_scheduled_posts.json");
  writeFileSync(file, JSON.stringify(queue, null, 2));
  const proc = spawnSync(process.execPath, [SCHEDULER, ...args], {
    cwd: dir,
    encoding: "utf8",
    env: { ...process.env, BSKY_HANDLE: "", BSKY_APP_PASSWORD: "" },
  });
  return { ...proc, queueAfter: JSON.parse(readFileSync(file, "utf-8")) };
}

const BACKLOG = [
  { at: "2026-09-22T02:00:00Z", text: "older", kind: "root", posted: false, posted_at: null, uri: null, error: null },
  { at: "2026-09-22T02:10:00Z", text: "newer", kind: "root", posted: false, posted_at: null, uri: null, error: null },
];

test("e2e: a fresh backlog is refused, and nothing is marked posted", () => {
  const recent = new Date(Date.now() - 5 * 60 * 1000).toISOString();
  const queue = [{ ...BACKLOG[0], at: recent }, BACKLOG[1]];
  // A prior post 5 minutes ago, exactly the state a delayed cloud run sees.
  queue.push({ at: recent, text: "just posted", kind: "root", posted: true, posted_at: recent, uri: "at://x", error: null });

  const run = runScheduler(queue, ["--min-gap", "900"]);
  assert.equal(run.status, 0, run.stderr);
  assert.match(run.stdout, /Rate governor/);
  assert.match(run.stdout, /Posting nothing this run/);
  assert.equal(run.queueAfter.filter((i) => i && i.posted).length, 1, "only the pre-existing post stays posted");
  assert.ok(!run.stderr.includes("Missing Bluesky credentials"), "governor must decide before any auth");
});

test("e2e: the governor does not fire a backlog in one burst", () => {
  const recent = new Date(Date.now() - 60 * 1000).toISOString();
  const queue = [
    ...Array.from({ length: 40 }, (_, i) => ({
      at: new Date(Date.now() - (40 - i) * 15 * 60 * 1000).toISOString(),
      text: `backlog ${i}`,
      kind: "root",
      posted: false,
      posted_at: null,
      uri: null,
      error: null,
    })),
    { at: recent, text: "last one", kind: "root", posted: true, posted_at: recent, uri: "at://x", error: null },
  ];
  const run = runScheduler(queue, ["--min-gap", "900"]);
  assert.equal(run.status, 0, run.stderr);
  assert.equal(run.queueAfter.filter((i) => i && i.posted).length, 1);
  assert.ok(!run.stdout.includes("✅"), "no post may be made while the governor is cooling down");
});

test("e2e: dry run reports what the governor and the staleness rule would do", () => {
  const twoHoursAgo = new Date(Date.now() - 2 * 3600 * 1000).toISOString();
  const run = runScheduler(
    [{ at: twoHoursAgo, text: "old take", kind: "root", posted: false, posted_at: null, uri: null, error: null }],
    ["--dry", "--max-age-min", "60"]
  );
  assert.equal(run.status, 0, run.stderr);
  assert.match(run.stdout, /Dry run/);
  assert.match(run.stdout, /TOO STALE/);
  assert.match(run.stdout, /would be DROPPED/);
  assert.equal(run.queueAfter[0].posted, false, "a dry run must not touch the queue");
});

test("e2e: a stale item is dropped and recorded without needing credentials", () => {
  const threeHoursAgo = new Date(Date.now() - 3 * 3600 * 1000).toISOString();
  // min-gap 0 so the governor cannot mask the staleness path. No credentials
  // are provided on purpose: dropping stale work must not depend on auth.
  const run = runScheduler(
    [{ at: threeHoursAgo, text: "old take", kind: "root", posted: false, posted_at: null, uri: null, error: null }],
    ["--min-gap", "0", "--max-age-min", "60"]
  );
  assert.equal(run.status, 0, run.stderr);
  assert.match(run.stdout, /Dropping/);
  assert.ok(!run.stderr.includes("Missing Bluesky credentials"), "a fully stale backlog must clean up without auth");
  assert.equal(run.queueAfter[0].skipped, true);
  assert.equal(run.queueAfter[0].posted, false);
  assert.match(run.queueAfter[0].error, /skipped/);
});

test("e2e: an already-skipped item is not handled again", () => {
  const threeHoursAgo = new Date(Date.now() - 3 * 3600 * 1000).toISOString();
  const run = runScheduler(
    [{ at: threeHoursAgo, text: "old take", kind: "root", posted: false, skipped: true, posted_at: null, uri: null, error: "skipped: 180 min late" }],
    ["--min-gap", "0", "--max-age-min", "60"]
  );
  assert.equal(run.status, 0, run.stderr);
  assert.match(run.stdout, /Nothing to do/);
});

test("e2e: bad flag values fall back to the safe default instead of disabling the guard", () => {
  const recent = new Date(Date.now() - 5 * 60 * 1000).toISOString();
  const run = runScheduler(
    [{ at: recent, text: "t", kind: "root", posted: false, posted_at: null, uri: null, error: null },
     { at: recent, text: "p", kind: "root", posted: true, posted_at: recent, uri: "at://x", error: null }],
    ["--min-gap", "banana"]
  );
  assert.equal(run.status, 0, run.stderr);
  assert.match(run.stdout, /Rate governor/, "a junk value must not open the floodgates");
});
