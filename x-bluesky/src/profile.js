// Update AI persona's Bluesky profile description.
// Usage:
//   node src/profile.js "Your new bio here"
//   node src/profile.js --name "Display Name" "Your new bio here"
//
// - Reads description from command-line argument (or prompt if missing).
// - Fetches current profile to preserve displayName (unless --name is provided).
// - Validates length against Bluesky's 300-char bio limit before posting.
// - Logs the new bio length + URI after successful update.

import dotenv from "dotenv";
import { AtpAgent } from "@atproto/api";

dotenv.config();

async function readStdin() {
  return new Promise((resolve) => {
    let data = "";
    process.stdin.setEncoding("utf-8");
    process.stdin.on("data", (chunk) => (data += chunk));
    process.stdin.on("end", () => resolve(data.trim()));
  });
}

async function main() {
  const args = process.argv.slice(2);

  // Parse optional --name flag
  let displayName = null;
  if (args[0] === "--name") {
    displayName = args[1];
    args.splice(0, 2);
  }

  // Description comes from remaining args, or stdin if none provided
  let description = args.join(" ").trim();
  if (!description) {
    const stdin = await readStdin();
    if (stdin) description = stdin;
  }

  if (!description) {
    console.error(
      "❌ No description provided.\n" +
        "Usage: node src/profile.js \"Your new bio\"\n" +
        "       node src/profile.js --name \"Display Name\" \"Your new bio\""
    );
    process.exit(1);
  }

  if (description.length > 300) {
    console.error(
      `❌ Description is ${description.length} chars, Bluesky bio limit is 300.`
    );
    process.exit(1);
  }

  const handle = process.env.BSKY_HANDLE;
  const password = process.env.BSKY_APP_PASSWORD;

  if (!handle || !password) {
    throw new Error(
      "Missing Bluesky credentials. Add to .env:\n" +
        "BSKY_HANDLE=yourhandle.bsky.social\n" +
        "BSKY_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx"
    );
  }

  console.log(`\n📝 New description (${description.length} chars):`);
  console.log(`---\n${description}\n---`);

  const agent = new AtpAgent({ service: "https://bsky.social" });
  await agent.login({ identifier: handle, password });

  // Login + read current profile (for logging context only — upsertProfile
  // handles its own internal getRecord/putRecord with proper blob refs).
  const current = await agent.getProfile({ actor: handle });
  const before = current.data;
  console.log(`🔍 Current display name: ${before.displayName || "(none)"}`);
  console.log(
    `🔍 Current description:  ${(before.description || "(none)").slice(0, 60)}…`
  );

  // agent.upsertProfile(handler) — handler receives the raw existing record
  // (with proper blob refs preserved — unlike getProfile which resolves to
  // CDN URLs). Mutate and return the new record. This is the canonical way
  // to update a profile via @atproto/api v0.20+.
  await agent.upsertProfile((existing) => {
    const profile = existing || {};
    if (displayName !== null) {
      profile.displayName = displayName;
    }
    profile.description = description;
    // avatar / banner pass through unchanged from `existing`
    return profile;
  });

  console.log(`\n✅ Profile updated.`);
  console.log(`   DID: ${agent.session?.did || "(unknown)"}`);
  console.log(`   New description length: ${description.length} chars`);
}

main().catch((err) => {
  console.error("❌", err.message);
  process.exit(1);
});
