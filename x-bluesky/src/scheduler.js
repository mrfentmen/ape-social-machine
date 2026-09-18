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
// Queue file: bsky_scheduled_posts.json
//   Each item:
//     {
//       at: "2026-07-14T14:30:00Z",     // ISO UTC timestamp
//       text: "post body...",             // ≤300 chars
//       kind: "root" | "reply",
//       target_uri?: "at://...",          // required for kind === "reply"
//       posted: false,
//       posted_at?: null,
//       uri?: null,
//       error?: null
//     }
//
// Posts marked posted: true are skipped on subsequent runs. Already-
// overdue posts at boot fire immediately. Failed posts set error and
// stay unposted so the operator can retry. Notification check between
// posts via --check-between (uses engage.js style API).

import dotenv from "dotenv";
import { AtpAgent } from "@atproto/api";
import { appendFileSync, existsSync, readFileSync, writeFileSync } from "fs";

dotenv.config();

const QUEUE_FILE = "bsky_scheduled_posts.json";
const POSTS_LOG = "bsky_posts_sent.txt";

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

async function postRoot(agent, item) {
  const r = await agent.post({ text: item.text });
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

async function cmdRun(dryRun, checkBetween, maxWaitSec = 0) {
  let queue = loadQueue().filter((i) => i && !i.posted);
  if (queue.length === 0) {
    console.log("Nothing to do — queue is empty or all posts marked posted.");
    return;
  }
  queue.sort((a, b) => Date.parse(a.at) - Date.parse(b.at));

  if (dryRun) {
    console.log("🔍 Dry run — no posts will be made.");
    for (const item of queue) {
      const delay = Date.parse(item.at) - Date.now();
      const when =
        delay <= 0
          ? `OVERDUE by ${Math.round(-delay / 1000)}s — would fire NOW`
          : `in ${Math.round(delay / 1000)}s (${new Date(item.at).toISOString()})`;
      console.log(`[${item.kind}] ${when}: "${item.text.slice(0, 80)}…"`);
    }
    return;
  }

  const agent = await getAgent();
  for (const [i, item] of queue.entries()) {
    const delay = Date.parse(item.at) - Date.now();
    if (delay > maxWaitSec * 1000) {
      console.log(
        `⏭️ Skipping ${item.kind} due ${item.at} — too far out (max wait ${maxWaitSec}s): "${item.text.slice(0, 60)}…"`
      );
      continue;
    }
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
      console.log(`✅ ${i + 1}/${queue.length} posted → ${item.uri}`);
    } catch (err) {
      item.error = err.message;
      console.log(`❌ ${i + 1}/${queue.length} FAILED: ${err.message}`);
    }
    saveQueue(loadQueue().map((existing) => {
      const matches = existing.at === item.at && existing.text === item.text;
      return matches ? item : existing;
    }));

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
  console.log(`\nDone. Fired ${queue.filter((i) => i.posted).length}/${queue.length} posts from queue.`);
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
  return cmdRun(dryRun, checkBetween, maxWait);
}

main().catch((err) => {
  console.error("❌", err.message);
  process.exit(1);
});
