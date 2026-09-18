// One-time login with stealth (avoids X bot detection).
// Run: npm run login

import { chromium } from "playwright-extra";
import StealthPlugin from "puppeteer-extra-plugin-stealth";

chromium.use(StealthPlugin());

const SESSION_FILE = "x-session.json";

async function login() {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  await page.goto("https://x.com/login");
  console.log("🔐 Log in to @yourhandle, then press Enter in this terminal...");

  await new Promise((resolve) => {
    process.stdin.once("data", () => resolve());
  });

  await page.waitForTimeout(1000);

  if (page.url().includes("login")) {
    console.log("⚠️  Still on login page. Try again.");
    await browser.close();
    process.exit(1);
  }

  await page.context().storageState({ path: SESSION_FILE });
  console.log(`✅ Session saved to ${SESSION_FILE}`);
  await browser.close();
}

login().catch((err) => {
  console.error("❌", err.message);
  process.exit(1);
});
