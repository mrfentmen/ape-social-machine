// Schedule posts to fire at specific UTC times — designed for the
// "operator is asleep, account still moves" use case. Single-process,
// exits when the queue is empty.
//
// Usage:
//   node src/scheduler.js                     (run the queue, fire as due)
//   node src/scheduler.js --dry               (preview what would fire when)
//   node src/scheduler.js add --at ISO --text "..."   (add a root post)
//   node src/scheduler.js add --at ISO --reply-to at://uri --text "..."
//   node src/scheduler.js list               (show queue status)
//   node src/scheduler.js clear              (wipe queue)
//
// Rate limiting (see rate_governor.js for why these exist):
//   --min-gap SEC    floor between two posts on the account, measured against
//                    the newest posted_at in the queue so it holds across the
//                    cloud workflow's once-a-minute re-invocation.
//                    Default 900 (the intended 15 minute cadence). 0 disables.
//   --max-posts N    most queue items this one invocation may handle.
//                    Default 6. 0 means no limit.
//   --max-age-min M  drop a post that is more than M minutes late instead of
//                    firing it late. Default 0 (disabled) so removing content is
//                    always an explicit choice.
//
// Queue file: bsky_scheduled_posts.json
//   Each item:
//     {
//       at: "2026-07-14T14:30:00Z",     // ISO UTC timestamp
//       text: "post body...",             // ≤300 chars (1024 for video posts)
//       kind: "root" | "reply",
//       target_uri?: "at://...",          // required for kind === "reply"
//       video_url?: "https://...mp4",     // optional: attach a video
//       aspect?: { width, height },       // required with video_url
//       alt?: "...",                      // optional video description
//       posted: false,
//       posted_at?: null,
//       uri?: null,
//       error?: null
//     }
//
// Video posts upload the file to the PDS with uploadBlob and embed it as
// app.bsky.embed.video. Bluesky allows one video per post; the file has to be
// mp4 and within the video service limits (10 minutes, 300MB as of Aug 2026).
//
// Posts marked posted: true are skipped on subsequent runs. Already-
// overdue posts at boot fire immediately. Failed posts set error and
// stay unposted so the operator can retry. Notification check between
// posts via --check-between (uses engage.js style API).

import dotenv from "dotenv";
import { AtpAgent } from "@atproto/api";
import { appendFileSync, existsSync, readFileSync, writeFileSync } from "fs";
import { governorVerdict, staleness } from "./rate_governor.js";

dotenv.config();

const QUEUE_FILE = "bsky_scheduled_posts.json";
const POSTS_LOG = "bsky_posts_sent.txt";

// The account's intended cadence. A run posts nothing when the newest
// posted_at is closer than this, which is what stops a delayed cloud run from
// firing the whole backlog. See rate_governor.js.
const DEFAULT_MIN_GAP_SEC = 900;
const DEFAULT_MAX_POSTS = 6;

/** A non-negative numeric CLI flag, or the fallback when absent/invalid. */
function numFlag(argv, name, fallback) {
  const idx = argv.indexOf(name);
  if (idx === -1) return fallback;
  const value = Number(argv[idx + 1]);
  return Number.isFinite(value) && value >= 0 ? value : fallback;
}

async function getAgent() {
  const handle = process.env.BSKY_HANDLE;
  const password = process.env.BSKY_APP_PASSWORD;
  if (!handle || !password) {
    throw new Error(
      "Missing Bluesky credentials in .env\n" +
        "BSKY_HANDLE=yourhandle.bsky.social\n" +
        "BSKY_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx"
    );
  }
  const a = new AtpAgent({ service: "https://bsky.social" });
  await a.login({ identifier: handle, password });
  return a;
}

function loadQueue() {
  if (!existsSync(QUEUE_FILE)) return [];
  try {
    return JSON.parse(readFileSync(QUEUE_FILE, "utf-8"));
  } catch (err) {
    console.error(`❌ Queue file is malformed JSON: ${err.message}`);
    process.exit(1);
  }
}

function saveQueue(q) {
  writeFileSync(QUEUE_FILE, JSON.stringify(q.filter((i) => i), null, 2));
}

function logPosted(text, kind, targetUri, resultUri) {
  const tag = kind === "reply" ? `reply_to=${targetUri}` : "root";
  appendFileSync(
    POSTS_LOG,
    `${new Date().toISOString()} | ${resultUri} | ${tag} | ${text.replace(/\n/g, " ")}\n`
  );
}

// -- Posting helpers ---------------------------------------------------------

async function buildVideoEmbed(agent, item) {
  const res = await fetch(item.video_url);
  if (!res.ok) {
    throw new Error(`could not fetch video (${res.status}) from ${item.video_url}`);
  }
  const bytes = new Uint8Array(await res.arrayBuffer());
  if (bytes.length === 0) {
    throw new Error(`video at ${item.video_url} was empty`);
  }
  const uploaded = await agent.uploadBlob(bytes, { encoding: "video/mp4" });
  const embed = {
    $type: "app.bsky.embed.video",
    video: uploaded.data.blob,
    aspectRatio: item.aspect || { width: 1080, height: 1920 },
  };
  if (item.alt) embed.alt = item.alt;
  return embed;
}

async function postRoot(agent, item) {
  const params = { text: item.text };
  if (item.video_url) {
    params.embed = await buildVideoEmbed(agent, item);
  }
  const r = await agent.post(params);
  item.uri = r.uri;
  item.posted_at = new Date().toISOString();
  logPosted(item.text, "root", null, r.uri);
  return r;
}

async function postReply(agent, item) {
  // Fetch target to get its cid + root reference.
  const fetched = await agent.app.bsky.feed.getPosts({ uris: [item.target_uri] });
  const target = fetched.data.posts[0];
  if (!target) {
    throw new Error(`Reply target not found at PDS: ${item.target_uri}`);
  }
  const targetCid = target.cid;
  const recordRoot = target.record?.reply?.root;
  let rootUri = item.target_uri;
  let rootCid = targetCid;
  if (recordRoot && recordRoot.uri && recordRoot.cid) {
    rootUri = recordRoot.uri;
    rootCid = recordRoot.cid;
  } else if (recordRoot && recordRoot.uri) {
    const rFetched = await agent.app.bsky.feed.getPosts({ uris: [recordRoot.uri] });
    const r = rFetched.data.posts[0];
    if (!r) throw new Error(`Root not found at PDS: ${recordRoot.uri}`);
    rootUri = r.uri;
    rootCid = r.cid;
  }
  const r = await agent.post({
    text: item.text,
    reply: {
      root: { uri: rootUri, cid: rootCid },
      parent: { uri: item.target_uri, cid: targetCid },
    },
  });
  item.uri = r.uri;
  item.posted_at = new Date().toISOString();
  logPosted(item.text, "reply", item.target_uri, r.uri);
  return r;
}

// -- Commands ---------------------------------------------------------------

async function cmdAdd(argv) {
  const rest = argv.slice(2); // skip "add"
  let at = null;
  let text = null;
  let targetUri = null;

  for (let i = 0; i < rest.length; i++) {
    if (rest[i] === "--at") {
      at = rest[++i];
    } else if (rest[i] === "--text") {
      text = rest.slice(i + 1).join(" ");
      break;
    } else if (rest[i] === "--reply-to") {
      targetUri = rest[++i];
    }
  }

  if (!at || !text) {
    console.error(
      "Usage: src/scheduler.js add --at <ISO UTC> [--reply-to at://uri] --text \"...\""
    );
    process.exit(1);
  }
  if (text.length > 300) {
    console.error(`❌ Text is ${text.length} chars, limit is 300.`);
    process.exit(1);
  }
  if (Number.isNaN(Date.parse(at))) {
    console.error(`❌ --at must be a parseable ISO timestamp, got: ${at}`);
    process.exit(1);
  }

  const item = {
    at,
    text,
    kind: targetUri ? "reply" : "root",
    target_uri: targetUri || null,
    posted: false,
    posted_at: null,
    uri: null,
    error: null,
  };
  const queue = loadQueue();
  queue.push(item);
  saveQueue(queue);
  console.log(`✅ Added ${item.kind} scheduled for ${at}: ${text.slice(0, 60)}…`);
}

function cmdList() {
  const queue = loadQueue();
  if (queue.length === 0) {
    console.log("Queue is empty.");
    return;
  }
  for (const [i, item] of queue.entries()) {
    const status = item.posted
      ? `✓ posted ${item.posted_at} → ${item.uri}`
      : item.skipped
      ? `🗑 skipped: ${item.error}`
      : item.error
      ? `✗ error: ${item.error}`
      : `⏳ due ${new Date(item.at).toISOString()}`;
    const kind = item.kind === "reply" ? `reply→ ${item.target_uri}` : "root";
    console.log(`${i + 1}. [${item.at}] [${kind}] ${status}\n   "${item.text.slice(0, 80)}${item.text.length > 80 ? "…" : ""}"`);
  }
}

function cmdClear() {
  saveQueue([]);
  console.log("Queue cleared.");
}

// Persist one item's new state back into the queue on disk. Matches on
// `at` + `text`, which is the queue's identity, and skips null rows so a
// malformed entry cannot crash the run.
function persistItem(item) {
  saveQueue(loadQueue().map((existing) => {
    if (!existing) return existing;
    const matches = existing.at === item.at && existing.text === item.text;
    return matches ? item : existing;
  }));
}

async function cmdRun(dryRun, checkBetween, maxWaitSec = 0, opts = {}) {
  const { minGapSec = 0, maxPosts = 0, maxAgeSec = 0 } = opts;
  const all = loadQueue();
  let queue = all.filter((i) => i && !i.posted && !i.skipped);
  if (queue.length === 0) {
    console.log("Nothing to do — queue is empty or all posts marked posted.");
    return;
  }
  queue.sort((a, b) => Date.parse(a.at) - Date.parse(b.at));

  if (dryRun) {
    console.log("🔍 Dry run — no posts will be made.");
    const gate = governorVerdict(all, { now: Date.now(), minGapSec });
    if (!gate.allowed) {
      console.log(
        `🛑 Rate governor would BLOCK this run: last post was ${Math.round(gate.sinceSec)}s ago, ` +
          `--min-gap is ${minGapSec}s (${Math.round(gate.waitSec)}s left).`
      );
    }
    for (const item of queue) {
      const delay = Date.parse(item.at) - Date.now();
      const late = staleness(item, { now: Date.now(), maxAgeSec });
      const when =
        delay <= 0
          ? `OVERDUE by ${Math.round(-delay / 1000)}s — would fire NOW`
          : `in ${Math.round(delay / 1000)}s (${new Date(item.at).toISOString()})`;
      const staleMark = late.stale
        ? ` [TOO STALE by ${Math.round(late.lateSec / 60)} min, --max-age-min ${Math.round(maxAgeSec / 60)}, would be DROPPED]`
        : "";
      console.log(`[${item.kind}] ${when}${staleMark}: "${item.text.slice(0, 80)}…"`);
    }
    return;
  }

  // Rate governor, read out of the queue itself so the limit holds across the
  // workflow's once-a-minute re-invocation rather than only inside this process.
  const gate = governorVerdict(all, { now: Date.now(), minGapSec });
  if (!gate.allowed) {
    console.log(
      `🛑 Rate governor: last post was ${Math.round(gate.sinceSec)}s ago and --min-gap is ` +
        `${minGapSec}s — ${Math.round(gate.waitSec)}s left. Posting nothing this run. ` +
        `${queue.length} item(s) still pending.`
    );
    return;
  }

  // Sweep the stale items before authenticating. Dropping a post that is hours
  // late is housekeeping: it needs no credentials, and a backlog that is
  // entirely stale must still get cleaned up when auth is broken.
  let dropped = 0;
  let notDue = 0;
  const due = [];
  for (const item of queue) {
    const delay = Date.parse(item.at) - Date.now();
    if (delay > maxWaitSec * 1000) {
      notDue++;
      continue;
    }
    const late = staleness(item, { now: Date.now(), maxAgeSec });
    if (late.stale) {
      dropped++;
      item.skipped = true;
      item.error =
        `skipped: ${Math.round(late.lateSec / 60)} min late, --max-age-min is ${Math.round(maxAgeSec / 60)}`;
      console.log(
        `🗑️ Dropping ${item.kind} due ${item.at} — ${item.error}. A post this late reads as a bot emptying a queue.`
      );
      persistItem(item);
      continue;
    }
    due.push(item);
  }
  if (notDue > 0) {
    console.log(
      `⏭️ ${notDue} item(s) not due yet — further out than --max-wait ${maxWaitSec}s.`
    );
  }
  if (due.length === 0) {
    console.log(`\nDone. Posted 0, dropped ${dropped} as too stale, nothing due to post.`);
    return;
  }

  // Authenticate only when there is actually something to post.
  const agent = await getAgent();
  let handled = 0;
  let posted = 0;
  for (const item of due) {
    if (maxPosts > 0 && handled >= maxPosts) {
      console.log(
        `⏸️ --max-posts ${maxPosts} reached; ${due.length - handled} due item(s) left for a later run.`
      );
      break;
    }
    handled++;
    const delay = Date.parse(item.at) - Date.now();
    if (delay > 0) {
      console.log(
        `⏳ Sleeping ${Math.round(delay / 1000)}s until ${item.at} for ${item.kind}: "${item.text.slice(0, 60)}…"`
      );
      await new Promise((r) => setTimeout(r, delay));
    }
    try {
      if (item.kind === "reply") {
        await postReply(agent, item);
      } else {
        await postRoot(agent, item);
      }
      item.posted = true;
      posted++;
      console.log(`✅ ${handled}/${due.length} posted → ${item.uri}`);
    } catch (err) {
      item.error = err.message;
      console.log(`❌ ${handled}/${due.length} FAILED: ${err.message}`);
    }
    persistItem(item);

    if (checkBetween) {
      try {
        const notifs = await agent.app.bsky.notification.listNotifications({ limit: 20 });
        const unseen = notifs.data.notifications.filter((n) => !n.read);
        console.log(`📡 ${unseen.length} unseen notifications between posts.`);
      } catch (err) {
        console.log(`⚠️ Could not check notifications: ${err.message}`);
      }
    }
  }
  console.log(
    `\nDone. Posted ${posted}, dropped ${dropped} as too stale, handled ${handled}/${due.length} due items.`
  );
}

// -- Entrypoint --------------------------------------------------------------

async function main() {
  const argv = process.argv;
  const cmd = argv[2];
  if (cmd === "add") return cmdAdd(argv);
  if (cmd === "list") return cmdList();
  if (cmd === "clear") return cmdClear();

  const dryRun = argv.includes("--dry");
  const checkBetween = argv.includes("--check-between");
  const maxWaitIdx = argv.indexOf("--max-wait");
  const maxWait = maxWaitIdx !== -1 ? Number(argv[maxWaitIdx + 1]) || 0 : 0;

  // Safe by default: a bare `node src/scheduler.js` can no longer empty a
  // backlog in one burst. See rate_governor.js for the measurements behind it.
  return cmdRun(dryRun, checkBetween, maxWait, {
    minGapSec: numFlag(argv, "--min-gap", DEFAULT_MIN_GAP_SEC),
    maxPosts: numFlag(argv, "--max-posts", DEFAULT_MAX_POSTS),
    maxAgeSec: numFlag(argv, "--max-age-min", 0) * 60,
  });
}

main().catch((err) => {
  console.error("❌", err.message);
  process.exit(1);
});
