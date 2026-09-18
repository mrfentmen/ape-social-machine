// Post to @yourhandle — uses ONE tab, posts multiple times.
// Start Chrome: /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug
// Then: npm run post          (posts once)
//       npm run post -- 3      (posts 3 times)

import { chromium } from "playwright";
import { existsSync, readFileSync, appendFileSync, writeFileSync } from "fs";
import { generatePost } from "./voice.js";

const CDP_URL = "http://127.0.0.1:9222";
const POSTS_LOG = "posts_sent.txt";

async function postTweet(page, text) {
  // Click the inline composer on home (force: true bypasses overlays)
  const composer = page.locator('[data-testid="tweetTextarea_0"]').first();
  await composer.click({ force: true });
  await page.waitForTimeout(300);
  await composer.fill(text);
  await page.waitForTimeout(300);

  // Click Post — try both home (tweetButtonInline) and modal (tweetButton)
  const postBtn = page.locator('[data-testid="tweetButtonInline"],[data-testid="tweetButton"]').first();
  await postBtn.click({ force: true });

  // Wait for composer to clear
  const didClear = await page.waitForFunction(
    () => {
      const c = document.querySelector('[data-testid="tweetTextarea_0"]');
      return !c || c.textContent === "" || c.innerText === "";
    },
    { timeout: 10000 }
  ).then(() => true).catch(() => false);

  if (didClear) process.stderr.write("✅\n");
  else process.stderr.write("⚠️\n");

  // Return home via SPA nav (click Home link — way faster than page.goto)
  await page.locator('a[aria-label="Home"]').first().click({ force: true }).catch(() => {});
  await page.waitForTimeout(1500);

  return didClear;
}

function logPost(id, text) {
  appendFileSync(POSTS_LOG, `${new Date().toISOString()} | ${id} | ${text.replace(/\n/g, " ")}\n`);
}

function getPastPosts() {
  if (!existsSync(POSTS_LOG)) { writeFileSync(POSTS_LOG, ""); return []; }
  return readFileSync(POSTS_LOG, "utf-8").trim().split("\n").filter(Boolean).map(line => {
    const parts = line.split(" | ");
    return parts.length >= 3 ? parts.slice(2).join(" | ") : line;
  });
}

async function main() {
  const count = Math.max(1, parseInt(process.argv[2]) || 1);
  
  const browser = await chromium.connectOverCDP(CDP_URL);
  const page = await browser.contexts()[0].newPage();
  
  // Navigate to home once
  await page.goto("https://x.com/home", { timeout: 15000 });
  await page.waitForTimeout(3000);
  
  if (page.url().includes("login")) {
    console.error("Not logged in.");
    await page.close();
    process.exit(1);
  }

  for (let i = 0; i < count; i++) {
    const pastPosts = getPastPosts();
    const tweet = generatePost(pastPosts);
    if (!tweet) { process.stderr.write("🤷 No fresh takes\n"); break; }

    process.stderr.write(`\n${i+1}/${count}: ${tweet.slice(0, 80)}...\n`);
    
    const ok = await postTweet(page, tweet.slice(0, 280));
    logPost(ok ? "posted" : "failed", tweet.slice(0, 280));
    
    // Wait between posts so X doesn't rate-limit
    if (i < count - 1) await page.waitForTimeout(3000);
  }

  await page.close();
  process.stderr.write("Done.\n");
}

main().catch(err => { console.error("❌", err.message); process.exit(1); });
