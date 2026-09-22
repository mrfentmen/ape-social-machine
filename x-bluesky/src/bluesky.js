// Post to Bluesky via the AT Protocol API.
// Requires BSKY_HANDLE and BSKY_APP_PASSWORD in .env
// Run: npm run bsky          (posts once)
//      npm run bsky -- 3      (posts 3 times)
//      npm run bsky:dry       (preview without posting)

import dotenv from "dotenv";
import { AtpAgent } from "@atproto/api";
import {
  existsSync,
  readFileSync,
  appendFileSync,
  writeFileSync,
} from "fs";
import { generatePost } from "./voice.js";

dotenv.config();

const POSTS_LOG = "bsky_posts_sent.txt";

// -- Auth --------------------------------------------------------------------

async function getAgent() {
  const handle = process.env.BSKY_HANDLE;
  const password = process.env.BSKY_APP_PASSWORD;

  if (!handle || !password) {
    throw new Error(
      "Missing Bluesky credentials. Add to .env:\n" +
        "BSKY_HANDLE=yourhandle.bsky.social\n" +
        "BSKY_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx"
    );
  }

  const agent = new AtpAgent({ service: "https://bsky.social" });
  await agent.login({ identifier: handle, password });
  return agent;
}

// -- Logging -----------------------------------------------------------------

// Line shape: "ISO | uri | tag | text", the same four fields scheduler.js
// writes. The tag is not decoration: bsky_build_queue.py reads this log to keep
// already-posted copy out of the draft pool, and a three field line was
// invisible to it, so those texts could be staged and posted a second time.
function logPost(uri, text, tag = "root") {
  const line = `${new Date().toISOString()} | ${uri} | ${tag} | ${text.replace(/\n/g, " ")}\n`;
  appendFileSync(POSTS_LOG, line);
}

// The post text out of one log line, for either shape the file holds:
//   "ISO | uri | tag | text"  (scheduler.js, and bluesky.js from now on)
//   "ISO | uri | text"        (older lines written by bluesky.js)
// Mirrors text_from_log_line() in bsky_build_queue.py so both readers agree.
function textFromLogLine(line) {
  const first = line.indexOf(" | ");
  if (first === -1) return line;
  const second = line.indexOf(" | ", first + 3);
  if (second === -1) return line.slice(first + 3);
  const rest = line.slice(second + 3);
  for (const tag of ["root", "failed"]) {
    if (rest.startsWith(`${tag} | `)) return rest.slice(tag.length + 3);
  }
  if (rest.startsWith("reply_to=")) {
    const sep = rest.indexOf(" | ");
    if (sep !== -1) return rest.slice(sep + 3);
  }
  return rest;
}

function getPastPosts() {
  if (!existsSync(POSTS_LOG)) {
    writeFileSync(POSTS_LOG, "");
    return [];
  }
  const lines = readFileSync(POSTS_LOG, "utf-8")
    .trim()
    .split("\n")
    .filter(Boolean);
  return lines.map(textFromLogLine);
}

// -- Main --------------------------------------------------------------------

async function main() {
  const dryRun = process.argv.includes("--dry");
  const count = Math.max(1, parseInt(process.argv[2]) || 1);

  // Authenticate once, reuse for all posts
  const agent = dryRun ? null : await getAgent();

  for (let i = 0; i < count; i++) {
    const pastPosts = getPastPosts();
    const post = generatePost(pastPosts);

    if (!post) {
      console.log("🤷 No fresh takes left.");
      break;
    }

    const finalText = post.slice(0, 300); // Bluesky limit is 300 chars
    console.log(`\n📝 Bluesky post ${i + 1}/${count} (${finalText.length} chars):`);
    console.log(`---\n${finalText}\n---`);

    if (dryRun) {
      console.log("🔍 Dry run — not posted.");
      continue;
    }

    try {
      const result = await agent.post({ text: finalText });
      logPost(result.uri || "posted", finalText);
      console.log(`✅ Posted: ${result.uri || "success"}`);
    } catch (err) {
      console.error(`❌ Failed: ${err.message}`);
      logPost("failed", finalText, "failed");
    }

    // Wait between posts
    if (i < count - 1) {
      console.log("⏳ Waiting 3s...");
      await new Promise((r) => setTimeout(r, 3000));
    }
  }

  console.log("\nDone.");
}

main().catch((err) => {
  console.error("❌", err.message);
  process.exit(1);
});
