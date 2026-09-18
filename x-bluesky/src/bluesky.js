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

function logPost(uri, text) {
  const line = `${new Date().toISOString()} | ${uri} | ${text.replace(/\n/g, " ")}\n`;
  appendFileSync(POSTS_LOG, line);
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
  return lines.map((line) => {
    const parts = line.split(" | ");
    return parts.length >= 3 ? parts.slice(2).join(" | ") : line;
  });
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
      logPost("failed", finalText);
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
