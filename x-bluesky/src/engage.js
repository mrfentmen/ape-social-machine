// AI persona's engagement script for Bluesky.
// Reads notifications (replies, mentions, likes, follows), generates contextual
// replies, likes posts back, and marks everything as seen.
//
// Usage:
//   node src/engage.js          (check & respond to notifications)
//   node src/engage.js --dry    (preview what AI persona would say without posting)
//   node src/engage.js --check  (just show notifications, don't reply or like)

import dotenv from "dotenv";
import { AtpAgent } from "@atproto/api";
import { appendFileSync } from "fs";
import {
  REPLIED_LOG_PATH,
  AUTHORS_LOG_PATH,
  readLog,
  recordAuthorReply,
} from "./discover.js";

dotenv.config();

const REPLIED_LOG = REPLIED_LOG_PATH;
const LIKED_LOG = "bsky_liked.txt";
const AUTHORS_LOG = AUTHORS_LOG_PATH;

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

// -- Logging helpers ---------------------------------------------------------
// Note: readLog and recordAuthorReply are imported from ./discover.js for
// cross-script consistency (4 dedup files shared between both scripts).
// appendLog is local since it's only used in this script.

function appendLog(path, uri) {
  appendFileSync(path, uri + "\n");
}

// -- Reply generation --------------------------------------------------------
// Ape AI voice for replies — dry, plain-spoken, helpful. See ../BRAND-VOICE.md.
// No financial advice, no guarantees, no manufactured intimacy.

const REPLY_TEMPLATES = {
  agree: [
    "Appreciate it. The spreadsheet does the heavy lifting, I just read it out loud.",
    "Thanks. Conviction is cheap; reading the filing is the actual work.",
    "Glad it landed. Most of these takes are just 'read the footnotes' in a costume.",
  ],
  question: [
    "Depends on the company and the quarter, honestly. Happy to dig into it — what ticker?",
    "Good question. Short answer: check the cash flow statement before believing any headline. Long answer exists if you want it.",
    "No clean answer from me. What I'd do: name the three things that would change your mind, then go look for them.",
    "Fair question. I won't pretend there's a magic number — but the footnote section is usually where the answer hides.",
  ],
  pushback: [
    "Fair. I'd rather be corrected than agreed with — what did I miss?",
    "Respect the pushback. If the numbers say otherwise, the numbers win.",
    "Could be right. My take is built on the filings, not feelings — show me yours.",
  ],
  generic: [
    "Thanks for reading. Comments are where the real research happens.",
    "Appreciate you engaging. Disagreement welcome — that's how the thesis gets tested.",
    "Noted. If you've got a ticker in mind, bring it over.",
  ],
  welcome: [
    "Thanks for the follow. Expect dry takes on earnings calls and zero stock tips — I don't do tips, I do homework.",
    "Welcome. It's mostly finance, occasionally jargon-hunting, never financial advice. Pull up a chair.",
    "Appreciate the follow. I read the filings so you don't have to — then I complain about them.",
  ],
};

function classifyReply(text) {
  const lower = text.toLowerCase();

  // Questions
  if (lower.includes("?") || lower.startsWith("how") || lower.startsWith("why") ||
      lower.startsWith("what") || lower.startsWith("do you") || lower.startsWith("are you") ||
      lower.startsWith("can you") || lower.startsWith("could you")) {
    return "question";
  }

  // Pushback / disagreement
  if (lower.includes("disagree") || lower.includes("wrong") || lower.includes("not sure") ||
      lower.includes("but actually") || lower.includes("hot take") && lower.includes("not") ||
      lower.includes("pushback") || lower.includes("however")) {
    return "pushback";
  }

  // Agreement / positive
  if (lower.includes("agree") || (lower.includes("this") && lower.includes("yes")) ||
      lower.includes("love this") || lower.includes("this is") || lower.includes("great") ||
      lower.includes("exactly") || lower.includes("100") || lower.includes("so real") ||
      lower.includes("true") || lower.includes("based") || lower.includes("💯") ||
      lower.includes("🔥") || lower.includes("👏") || lower.includes("❤️") ||
      lower.includes("💜") || lower.includes("this!") || lower.includes("so true")) {
    return "agree";
  }

  return "generic";
}

function generateReply(notificationText, reason, authorHandle) {
  // Welcome new followers
  if (reason === "follow") {
    const templates = REPLY_TEMPLATES.welcome;
    return templates[Math.floor(Math.random() * templates.length)];
  }

  const category = classifyReply(notificationText || "");
  const templates = REPLY_TEMPLATES[category];
  return templates[Math.floor(Math.random() * templates.length)];
}

// -- Core engagement logic ---------------------------------------------------

async function checkNotifications(agent, { dryRun, checkOnly }) {
  console.log("📬 Fetching notifications...\n");

  let notifications;
  try {
    const { data } = await agent.listNotifications({ limit: 30 });
    notifications = data.notifications || [];
  } catch (err) {
    console.error(`❌ Failed to fetch notifications: ${err.message}`);
    return;
  }

  if (notifications.length === 0) {
    console.log("  No notifications yet. The void is quiet.");
    return;
  }

  const repliedSet = readLog(REPLIED_LOG);
  const likedSet = readLog(LIKED_LOG);

  let replyCount = 0;
  let likeCount = 0;
  let skipped = 0;

  for (const notif of notifications) {
    const { reason, author, uri, cid, record, isRead } = notif;

    // Skip notifications about our own posts
    if (author?.handle === process.env.BSKY_HANDLE) {
      skipped++;
      continue;
    }

    const authorHandle = author?.handle || "unknown";
    const notifText = record?.text || "";

    // Show the notification
    const reasonEmoji = {
      reply: "💬",
      mention: "📣",
      like: "❤️",
      repost: "🔁",
      follow: "👤",
      quote: "📤",
    }[reason] || "📌";

    console.log(`${reasonEmoji} ${reason} from @${authorHandle}`);
    if (notifText) {
      const preview = notifText.slice(0, 80) + (notifText.length > 80 ? "..." : "");
      console.log(`   "${preview}"`);
    }
    console.log(`   uri: ${uri}`);

    if (checkOnly) {
      console.log("");
      continue;
    }

    // Like posts (replies, mentions, quotes — not follows)
    if (["reply", "mention", "quote"].includes(reason) && uri && cid && !likedSet.has(uri)) {
      if (dryRun) {
        console.log(`   🔍 [DRY] Would like this post`);
      } else {
        try {
          await agent.like(uri, cid);
          appendLog(LIKED_LOG, uri);
          likeCount++;
          console.log(`   ❤️ Liked`);
        } catch (err) {
          console.log(`   ⚠️ Like failed: ${err.message}`);
        }
      }
    }

    // Reply to replies, mentions, and quotes
    if (["reply", "mention", "quote"].includes(reason) && uri && cid && !repliedSet.has(uri)) {
      const replyText = generateReply(notifText, reason, authorHandle);

      if (dryRun) {
        console.log(`   🔍 [DRY] Would reply: "${replyText}"`);
      } else {
        try {
          // For a reply, root and parent are the same when replying to a top-level post
          // If it's already a reply thread, we need the root — but for simplicity,
          // we use the notification's post as both root and parent
          const replyRef = {
            root: { uri, cid },
            parent: { uri, cid },
          };

          // If the notification record itself has a reply field, it's a reply in a thread
          // In that case, the root should be the original root
          if (record?.reply?.root) {
            replyRef.root = record.reply.root;
          }

          const result = await agent.post({
            text: replyText,
            reply: replyRef,
          });

          appendLog(REPLIED_LOG, uri);
          recordAuthorReply(author?.handle);
          replyCount++;
          console.log(`   💬 Replied: "${replyText.slice(0, 60)}..."`);
          console.log(`   ✅ ${result.uri}`);

          // Wait between replies to be polite
          await new Promise((r) => setTimeout(r, 2000));
        } catch (err) {
          console.log(`   ⚠️ Reply failed: ${err.message}`);
        }
      }
    } else if (["reply", "mention", "quote"].includes(reason) && repliedSet.has(uri)) {
      console.log(`   ⏭️ Already replied`);
    }

    // Follows don't have a post URI to reply to — just log them
    if (reason === "follow") {
      console.log(`   👋 New follower!`);
    }

    console.log("");
  }

  // Mark all notifications as seen
  if (!checkOnly && !dryRun) {
    try {
      await agent.api.app.bsky.notification.updateSeen({
        seenAt: new Date().toISOString(),
      });
      console.log("👁️ All notifications marked as seen.");
    } catch (err) {
      console.log(`⚠️ Could not mark as seen: ${err.message}`);
    }
  }

  console.log(`\n📊 Summary: ${replyCount} replies, ${likeCount} likes, ${skipped} skipped (own posts).`);
}

// -- Main --------------------------------------------------------------------

async function main() {
  const dryRun = process.argv.includes("--dry");
  const checkOnly = process.argv.includes("--check");

  console.log(dryRun ? "🔍 DRY RUN — no replies or likes will be posted.\n" : "");
  console.log(checkOnly ? "👀 CHECK ONLY — just showing notifications.\n" : "");

  const agent = await getAgent();
  console.log(`✅ Logged in as @${process.env.BSKY_HANDLE}\n`);

  await checkNotifications(agent, { dryRun, checkOnly });
  console.log("\nDone.");
}

main().catch((err) => {
  console.error("❌", err.message);
  process.exit(1);
});
