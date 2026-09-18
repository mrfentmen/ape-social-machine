// Post raw, custom text to Bluesky — for when the company has something real to say.
// Usage:
//   node src/raw.js "Your text here"
//   node src/raw.js --dry "Your text here"      (preview only, posts nothing)
//   node src/raw.js "$(cat somefile.txt)"
//
// Reads text from command-line argument. Posts as-is (within 300 char limit).
// Guardrails (guardrails.js) run first: banned phrases abort the post.

import dotenv from "dotenv";
import { AtpAgent } from "@atproto/api";
import { appendFileSync } from "fs";
import { validateText } from "./guardrails.js";

dotenv.config();

const POSTS_LOG = "bsky_posts_sent.txt";

async function main() {
  const args = process.argv.slice(2);
  const dry = args.includes("--dry");
  const text = args.filter((a) => a !== "--dry").join(" ");

  if (!text || text.trim().length === 0) {
    console.error("❌ No text provided. Usage: node src/raw.js \"Your post text\"");
    process.exit(1);
  }

  if (text.length > 300) {
    console.error(`❌ Text is ${text.length} chars, Bluesky limit is 300. Trim it.`);
    process.exit(1);
  }

  console.log(`\n📝 Raw post (${text.length} chars):`);
  console.log(`---\n${text}\n---`);

  const check = validateText(text);
  if (!check.ok) {
    console.error(`🛑 Blocked by guardrails: banned phrase(s): ${check.hits.join(", ")}`);
    process.exit(1);
  }

  const handle = process.env.BSKY_HANDLE;
  const password = process.env.BSKY_APP_PASSWORD;

  if (!handle || !password) {
    throw new Error("Missing Bluesky credentials in .env");
  }

  if (dry) {
    console.log("🔍 Dry run — not posted.");
    return;
  }

  const agent = new AtpAgent({ service: "https://bsky.social" });
  await agent.login({ identifier: handle, password });

  const result = await agent.post({ text });
  const line = `${new Date().toISOString()} | ${result.uri} | ${text.replace(/\n/g, " ")}\n`;
  appendFileSync(POSTS_LOG, line);
  console.log(`✅ Posted: ${result.uri}`);
}

main().catch((err) => {
  console.error("❌", err.message);
  process.exit(1);
});
