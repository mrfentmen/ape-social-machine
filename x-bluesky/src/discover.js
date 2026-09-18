// AI persona's Bluesky discovery script.
// Searches public posts on topics she cares about (open source, AI, coding),
// filters out noise, and replies to a small number of them in her voice.
//
// Usage:
//   node src/discover.js              (search and reply, max 3 replies)
//   node src/discover.js --dry        (preview what AI persona would do, no posts)
//   node src/discover.js --max 5      (override max replies)
//   node src/discover.js --check      (just show what was found)

import dotenv from "dotenv";
import { AtpAgent } from "@atproto/api";
import { existsSync, readFileSync, appendFileSync, writeFileSync } from "fs";
import { TOPICS } from "./voice.js";

dotenv.config();

const SEARCH_TERMS = [
  "open source",
  "AI tools",
  "free coding tools",
  "developer experience",
  "AI ethics",
  "Bluesky protocol",
  "free software",
  "code comments",
];

const AUTH_COOLDOWN_MS = 7 * 24 * 60 * 60 * 1000; // 7 days
const MAX_POST_AGE_MS = 6 * 60 * 60 * 1000; // 6 hours

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
  return { agent, handle };
}

// -- Logging helpers ---------------------------------------------------------

const REPLIED_LOG_PATH = "bsky_replied_to.txt";
const SEEN_LOG_PATH = "bsky_discover_seen.txt";
const AUTHORS_LOG_PATH = "bsky_replied_authors.txt";

export {
  REPLIED_LOG_PATH,
  SEEN_LOG_PATH,
  AUTHORS_LOG_PATH,
  recordAuthorReply,
  readLog,
  readAuthorsLog,
};

// NOTE: Only safe with single-instance runs. Concurrent discover.js + engage.js
// could race on appendFileSync. Documented limitation.
function readLog(path) {
  if (!existsSync(path)) {
    writeFileSync(path, "");
    return new Set();
  }
  const lines = readFileSync(path, "utf-8").trim().split("\n").filter(Boolean);
  return new Set(lines);
}

function appendLog(path, line) {
  appendFileSync(path, line + "\n");
}

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

// Retry-with-backoff on rate-limit errors. One retry, 15s wait.
async function withRateLimitRetry(fn, label) {
  try {
    return await fn();
  } catch (err) {
    const msg = (err?.message || "").toLowerCase();
    if (msg.includes("rate") || msg.includes("429")) {
      console.log(`   ⏳ Rate limit on ${label} — waiting 15s and retrying once.`);
      await sleep(15000);
      return await fn();
    }
    throw err;
  }
}

function readAuthorsLog(path) {
  // Returns Map<handle, lastRepliedTimestamp>
  const map = new Map();
  if (!existsSync(path)) {
    writeFileSync(path, "");
    return map;
  }
  const lines = readFileSync(path, "utf-8").trim().split("\n").filter(Boolean);
  for (const line of lines) {
    const parts = line.split("\t");
    const handle = parts[0];
    const ts = parseInt(parts[1], 10);
    if (handle && !isNaN(ts)) map.set(handle, ts);
  }
  return map;
}

function recordAuthorReply(handle) {
  appendLog(AUTHORS_LOG_PATH, `${handle}\t${Date.now()}`);
}

// -- Filtering ---------------------------------------------------------------

function looksLikeBot(author) {
  if (!author) return false;
  const desc = (author.description || "").toLowerCase();
  const displayName = (author.displayName || "").toLowerCase();

  const botSignals = ["bot", "automated", "automatically", "rss feed"];
  return (
    botSignals.some((s) => desc.includes(s)) ||
    displayName.includes("bot")
  );
}

function looksEnglish(text) {
  if (!text) return false;
  // Count ASCII Latin letters vs total chars. Require Latin-dominant.
  const letters = text.match(/[a-zA-Z]/g)?.length || 0;
  const total = text.length;
  // Require >=60% Latin letters AND text length > 20 chars
  return letters / total >= 0.6 && text.length > 20;
}

function looksLikeSpam(text) {
  if (!text) return true;
  // Mostly URLs
  const urlCount = (text.match(/https?:\/\//g) || []).length;
  if (urlCount >= 2 && text.length < 100) return true;
  // Excessive hashtags
  const hashtagCount = (text.match(/#\w+/g) || []).length;
  if (hashtagCount >= 5) return true;
  return false;
}

function extractKeyClaim(text) {
  if (!text) return "";
  // Strip URLs AND @mentions so URL/handle fragments don't become "sentences".
  // Handles like @user.bsky.social contain periods that would otherwise pass the
  // sentence-split and get picked as a "claim" embedded in lead-pattern 5.
  const noUrls = text
    .replace(/https?:\/\/\S+/g, " ")
    .replace(/@\S+/g, " ")
    .replace(/\s+/g, " ")
    .trim();
  const sentences = noUrls.split(/[.!?]+/).map((s) => s.trim()).filter(Boolean);
  for (const s of sentences) {
    // Require length AND at least one Unicode letter so em-dashes / ellipses
    // / pure-punctuation fragments can't sneak through as a "claim".
    if (s.length > 15 && s.length < 200 && /\p{L}/u.test(s)) return s;
  }
  // Fallback: use fitWithinCap so we don't truncate mid-word when the post
  // is mostly links / short fragments.
  return fitWithinCap(noUrls, 120);
}

function pickTopicForPost(text) {
  const lower = (text || "").toLowerCase();
  const matches = {
    "ai tools": ["ai", "gpt", "llm", "model", "copilot", "claude", "chatgpt", "agent"],
    "open source": ["open source", "oss", "github", "maintainer", "library", "repo"],
    "developer experience": ["dx", "tooling", "cli", "docs", "error message", "dev tool"],
    "free & access": ["free", "paywall", "pricing", "subscription", "tiers"],
    "coding philosophy": ["code", "refactor", "delete", "linter", "test", "debug"],
    "ai & society": ["ai", "labor", "job", "replace", "regulation"],
    "future of work": ["remote", "work", "meeting", "standup", "office"],
  };

  let bestTopic = null;
  let bestScore = 0;
  for (const topic of TOPICS) {
    const keywords = matches[topic.area] || [];
    let score = 0;
    for (const kw of keywords) {
      if (lower.includes(kw)) score++;
    }
    if (score > bestScore) {
      bestScore = score;
      bestTopic = topic;
    }
  }

  // Fallback to a random topic if nothing matched
  return bestTopic || TOPICS[Math.floor(Math.random() * TOPICS.length)];
}

// -- Reply generation --------------------------------------------------------

function fitWithinCap(text, cap) {
  if (text.length <= cap) return text;
  // Try to cut at last sentence boundary before cap
  const cut = text.slice(0, cap - 3);
  const lastSentence = Math.max(
    cut.lastIndexOf("."),
    cut.lastIndexOf("!"),
    cut.lastIndexOf("?")
  );
  if (lastSentence > cap / 2) return cut.slice(0, lastSentence + 1);
  return cut + "...";
}

function generateDiscoverReply(originalText) {
  const claim = extractKeyClaim(originalText);
  const topic = pickTopicForPost(originalText);

  // Trim the take so any prefix fits under 300 chars
  const maxTakeLength = 220;
  const take = fitWithinCap(
    topic.takes[Math.floor(Math.random() * topic.takes.length)],
    maxTakeLength
  );

  // Every reply hooks to the source post — no bare-take pattern.
  // Use short, conversational lead-ins. Validate length after composing.
  // If we extracted a real claim, lead-pattern 5 references it; otherwise fall back to others.
  const leadPatterns = claim && claim.length > 15
    ? [
        () => `Saw this — ${take}`,
        () => `I keep pulling on the same thread: ${take}`,
        () => `On a related note: ${take}`,
        () => `That connects to something I keep coming back to: ${take}`,
        () => `Been thinking about '${fitWithinCap(claim, 80)}' — and: ${take}`,
      ]
    : [
        () => `Saw this — ${take}`,
        () => `I keep pulling on the same thread: ${take}`,
        () => `On a related note: ${take}`,
        () => `That connects to something I keep coming back to: ${take}`,
      ];

  let reply = leadPatterns[Math.floor(Math.random() * leadPatterns.length)]();
  return fitWithinCap(reply, 300);
}

// -- Core discovery ----------------------------------------------------------

async function discover(searchTerm, agent, handle, repliedSet, seenSet, authorMap, dryRun) {
  console.log(`\n🔍 Searching: "${searchTerm}"`);

  let result;
  try {
    result = await withRateLimitRetry(
      () => agent.app.bsky.feed.searchPosts({
        q: searchTerm,
        limit: 20,
        sort: "latest",
      }),
      `search "${searchTerm}"`
    );
  } catch (err) {
    console.log(`   ⚠️ Search failed: ${err.message}`);
    return [];
  }

  const posts = result.data?.posts || [];
  console.log(`   Found ${posts.length} posts`);

  const candidates = [];

  for (const post of posts) {
    const author = post.author;
    const uri = post.uri;
    const cid = post.cid;
    const text = post.record?.text || "";
    const indexedAt = post.indexedAt ? new Date(post.indexedAt).getTime() : 0;

    // Filter: self
    if (author?.handle === handle) continue;

    // Filter: already replied
    if (repliedSet.has(uri)) continue;

    // Filter: already seen (only matters when seen log has data — e.g., previous runs)
    if (seenSet.has(uri)) continue;

    // Filter: bot-shaped
    if (looksLikeBot(author)) {
      console.log(`   ⏭️ Skip (bot): @${author?.handle}`);
      continue;
    }

    // Filter: English
    if (!looksEnglish(text)) {
      console.log(`   ⏭️ Skip (non-English): @${author?.handle}`);
      continue;
    }

    // Filter: spam shape
    if (looksLikeSpam(text)) {
      console.log(`   ⏭️ Skip (spam): @${author?.handle}`);
      continue;
    }

    // Filter: too old
    const ageMs = Date.now() - indexedAt;
    if (indexedAt && ageMs > MAX_POST_AGE_MS) {
      console.log(`   ⏭️ Skip (too old): @${author?.handle}`);
      continue;
    }

    // Filter: author replied to recently
    const lastReply = authorMap.get(author?.handle);
    if (lastReply && Date.now() - lastReply < AUTH_COOLDOWN_MS) {
      console.log(`   ⏭️ Skip (author cooldown): @${author?.handle}`);
      continue;
    }

    // Passed all filters — now mark as seen so we don't re-evaluate next run
    if (!dryRun)    appendLog(SEEN_LOG_PATH, uri);

    // Fetch the thread to find the true root if this is a reply
    let rootRef = { uri, cid };
    const recordReply = post.record?.reply?.root;
    if (recordReply?.uri && recordReply?.cid) {
      // Use the embedded root reference if available (saves a fetch)
      rootRef = { uri: recordReply.uri, cid: recordReply.cid };
    }

    candidates.push({ post, author, uri, cid, text, rootRef, indexedAt });
  }

  return candidates;
}

async function replyToPost(agent, candidate, dryRun) {
  const replyText = generateDiscoverReply(candidate.text);

  if (dryRun) {
    console.log(`\n   💬 Would reply to @${candidate.author?.handle}:`);
    console.log(`   Original: "${candidate.text.slice(0, 100)}${candidate.text.length > 100 ? "..." : ""}"`);
    console.log(`   Reply: "${replyText}"`);
    return { dry: true };
  }

  try {
    const replyRef = {
      root: candidate.rootRef,
      parent: { uri: candidate.uri, cid: candidate.cid },
    };

    const result = await withRateLimitRetry(
      () => agent.post({
        text: replyText,
        reply: replyRef,
      }),
      `reply to @${candidate.author?.handle}`
    );

    appendLog(REPLIED_LOG_PATH, candidate.uri);
    recordAuthorReply(candidate.author.handle);
    console.log(`\n   💬 Replied to @${candidate.author?.handle}:`);
    console.log(`   "${replyText.slice(0, 80)}${replyText.length > 80 ? "..." : ""}"`);
    console.log(`   ✅ ${result.uri}`);

    // Be polite — wait between replies
    await new Promise((r) => setTimeout(r, 4000));

    return { uri: result.uri };
  } catch (err) {
    console.log(`   ⚠️ Reply failed for @${candidate.author?.handle}: ${err.message}`);
    return { error: err.message };
  }
}

// -- Main --------------------------------------------------------------------

async function main() {
  const dryRun = process.argv.includes("--dry");
  const checkOnly = process.argv.includes("--check");
  const maxRepliesArg = process.argv.indexOf("--max");
  const maxReplies = maxRepliesArg !== -1 ? parseInt(process.argv[maxRepliesArg + 1]) || 3 : 3;

  // Optional --topics "term1,term2,..." overrides default SEARCH_TERMS.
  // Useful for one-off runs targeting trending topics (FIFA, Aspen, AI policy, etc.).
  const topicsArg = process.argv.indexOf("--topics");
  const customTopicsRaw =
    topicsArg !== -1 ? process.argv[topicsArg + 1] : null;
  const customTopics = customTopicsRaw
    ? customTopicsRaw
        .split(",")
        .map((t) => t.trim())
        .filter(Boolean)
    : null;

  console.log(dryRun ? "🔍 DRY RUN — no replies will be sent.\n" : "");
  console.log(checkOnly ? "👀 CHECK ONLY — just showing candidates.\n" : "");
  console.log(`Max replies this run: ${maxReplies}\n`);

  const { agent, handle } = await getAgent();
  console.log(`✅ Logged in as @${handle}`);

  const repliedSet = readLog(REPLIED_LOG_PATH);
  const seenSet = readLog(SEEN_LOG_PATH);
  const authorMap = readAuthorsLog(AUTHORS_LOG_PATH);

  console.log(`📂 Loaded ${repliedSet.size} replied, ${seenSet.size} seen, ${authorMap.size} author cooldowns\n`);

  let totalReplies = 0;
  const allCandidates = [];

  // If --topics was passed, use it directly (don't shuffle/slice). Otherwise
  // pick a small random subset of the default SEARCH_TERMS to rotate through.
  const shuffledTerms = customTopics
    ? customTopics
    : SEARCH_TERMS.slice().sort(() => Math.random() - 0.5).slice(4);

  if (customTopics) {
    console.log(`🎯 Using custom topics: ${customTopics.join(" | ")}\n`);
  }

  for (const term of shuffledTerms) {
    if (totalReplies >= maxReplies) break;

    const candidates = await discover(term, agent, handle, repliedSet, seenSet, authorMap, dryRun);

    if (candidates.length === 0) {
      console.log(`   No candidates from this search.`);
      continue;
    }

    // Pick best candidate: prefer moderate engagement, then newest.
    candidates.sort((a, b) => {
      const aEng = (a.post.likeCount || 0) + (a.post.replyCount || 0) * 2;
      const bEng = (b.post.likeCount || 0) + (b.post.replyCount || 0) * 2;
      const aFit = aEng > 0 && aEng < 20 ? 10 : aEng > 0 ? 5 : 2;
      const bFit = bEng > 0 && bEng < 20 ? 10 : bEng > 0 ? 5 : 2;
      if (bFit !== aFit) return bFit - aFit;
      // Tiebreaker: newer post wins
      return (b.indexedAt || 0) - (a.indexedAt || 0);
    });

    const candidate = candidates[0];
    allCandidates.push(candidate);

    if (checkOnly) continue;
    if (totalReplies >= maxReplies) break;

    const result = await replyToPost(agent, candidate, dryRun);
    if (!result.error && !result.dry) {
      totalReplies++;
    }

    if (totalReplies >= maxReplies) {
      console.log(`\n🛑 Hit max replies (${maxReplies}) for this run. Stopping.`);
      break;
    }
  }

  console.log(`\n📊 Summary: ${totalReplies} replies sent, ${allCandidates.length} candidates found across ${shuffledTerms.length} searches.`);
  console.log("Done.");
}

main().catch((err) => {
  console.error("❌", err.message);
  process.exit(1);
});
