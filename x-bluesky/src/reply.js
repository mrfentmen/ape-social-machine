// Reply to an existing post on Bluesky.
// Usage:
//   node src/reply.js <target_at_uri> "reply text content"
//   node src/reply.js --dry <target_at_uri> "reply text content"
//
// Reads target URI (the first argv starting with at://) and reply text
// (everything else, joined with spaces). Validates length against the
// 300-char Bluesky post limit before posting. Resolves the target's cid
// + root reply-ref via getPosts so the reply threads correctly even
// if the target is itself a reply in a thread.
//
// Logs each successful reply to bsky_posts_sent.txt with the
// "reply_to=<target>" prefix.

import dotenv from "dotenv";
import { AtpAgent } from "@atproto/api";
import { appendFileSync } from "fs";

dotenv.config();

const POSTS_LOG = "bsky_posts_sent.txt";

// -- Auth --------------------------------------------------------------------

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

  const agent = new AtpAgent({ service: "https://bsky.social" });
  await agent.login({ identifier: handle, password });
  return agent;
}

// -- Args --------------------------------------------------------------------

function parseArgs(argv) {
  let dryRun = false;
  // argv is process.argv — first two elements are "node" and the script path.
  // Skip them so we only operate on real user-supplied args.
  const rest = argv.slice(2);
  const idx = rest.indexOf("--dry");
  if (idx !== -1) {
    dryRun = true;
    rest.splice(idx, 1);
  }

  // Find target URI by value, not by index — index-based filtering with
  // a single-element array doesn't reliably yield the right text parts.
  const targetUri = rest.find((a) => a.startsWith("at://"));
  if (!targetUri) {
    throw new Error(
      "No target URI found in args.\n" +
        'Usage: node src/reply.js <at://uri> "reply text"\n' +
        '       node src/reply.js --dry <at://uri> "reply text"'
    );
  }

  // Text is everything else, joined with spaces. If nothing remains,
  // we have no reply content.
  const text = rest.filter((a) => a !== targetUri).join(" ").trim();
  if (!text) throw new Error("Empty reply text.");
  if (text.length > 300) {
    throw new Error(
      `Reply is ${text.length} chars, Bluesky limit is 300. Trim it.`
    );
  }

  return { dryRun, targetUri, text };
}

// -- Main --------------------------------------------------------------------

async function main() {
  let args;
  try {
    args = parseArgs(process.argv);
  } catch (err) {
    console.error(`❌ ${err.message}`);
    process.exit(1);
  }

  console.log(`\n📝 Reply (${args.text.length} chars):`);
  console.log(`   target: ${args.targetUri}`);
  console.log(`---\n${args.text}\n---`);

  if (args.dryRun) {
    console.log("🔍 Dry run — no post made, no login required.");
    return;
  }

  const agent = await getAgent();

  // Resolve target cid + root. The target may itself be a reply in
  // a thread — in that case its record.reply.root holds the true root
  // we should thread under; otherwise root = target itself.
  const fetched = await agent.app.bsky.feed.getPosts({
    uris: [args.targetUri],
  });
  const target = fetched.data.posts[0];
  if (!target) {
    throw new Error(`Target post not found at PDS: ${args.targetUri}`);
  }

  const targetCid = target.cid;
  const recordRoot = target.record?.reply?.root;

  let rootUri = args.targetUri;
  let rootCid = targetCid;
  if (recordRoot && recordRoot.uri && recordRoot.cid) {
    rootUri = recordRoot.uri;
    rootCid = recordRoot.cid;
  } else if (recordRoot && recordRoot.uri) {
    // Some references ship with only the URI (no pre-resolved cid).
    // Look it up; if the PDS has no copy, fail loudly rather than silently
    // threading the reply under the parent as if it were the root.
    const rootFetched = await agent.app.bsky.feed.getPosts({
      uris: [recordRoot.uri],
    });
    const r = rootFetched.data.posts[0];
    if (!r) {
      throw new Error(
        `Root post not found at PDS: ${recordRoot.uri}. ` +
          `Cannot thread reply without a resolved root cid.`
      );
    }
    rootUri = r.uri;
    rootCid = r.cid;
  }

  const replyRef = {
    root: { uri: rootUri, cid: rootCid },
    parent: { uri: args.targetUri, cid: targetCid },
  };

  const result = await agent.post({
    text: args.text,
    reply: replyRef,
  });

  appendFileSync(
    POSTS_LOG,
    `${new Date().toISOString()} | ${result.uri} | reply_to=${args.targetUri} | ${args.text.replace(/\n/g, " ")}\n`
  );

  console.log(`✅ Reply posted: ${result.uri}`);
  console.log(`   root: ${rootUri}`);
  console.log(`   parent: ${args.targetUri}`);
}

main().catch((err) => {
  console.error("❌", err.message);
  process.exit(1);
});
