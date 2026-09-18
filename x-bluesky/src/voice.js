// Ape AI (AskApe.com) posting brain.
// Voice: see ../BRAND-VOICE.md — sharp, dry, finance-literate, anti-BS.
// Generates posts for Bluesky (300 chars) and X (280 chars).
// All output passes guardrails before posting.

import { validateText } from "./guardrails.js";

// -- TOPIC POOLS ---------------------------------------------------------------
// Every "take" is a standalone post idea written in the brand voice.
// Safety: no price predictions, no invented figures, no guarantees —
// specific numbers belong in hand-written posts, not evergreen templates.

const TOPICS = [
  {
    area: "retail investing reality",
    takes: [
      "Your brokerage app shows you your balance. It has never once shown you the fees you paid to have that balance. Ask about the fees.",
      "Retail investors don't lose because they're dumb. They lose because the tools they get are built to look at, not to think with.",
      "The bar for financial research used to be a terminal that costs more than your rent. That's the only reason 'do your own research' used to be a joke.",
      "Nobody reads a 10-K. That's fair. But an AI can read it for you and tell you the three lines that matter. That's not cheating, that's delegating.",
      "Your portfolio is a story about what you believed six months ago. Worth rereading occasionally.",
      "The most expensive habit in investing isn't panic selling. It's never checking your assumptions in the first place.",
    ],
  },
  {
    area: "corporate jargon fatigue",
    takes: [
      "The earnings call said 'headwinds' eleven times. A headwind is weather. This is a spreadsheet. Numbers, please.",
      "'Synergies' is what a company calls it when two spreadsheets get married and the kids are layoffs.",
      "Quarterly earnings calls are corporate ASMR for people who own six shares and a dream.",
      "Every company is 'repositioning for growth.' Translation: the last position didn't work.",
      "'We're taking a disciplined approach to capital allocation' means they spent it and will tell you how next quarter.",
    ],
  },
  {
    area: "AI in finance, minus the hype",
    takes: [
      "An AI that tells you what you want to hear about your portfolio is a mirror, not a tool. Ask it what you're missing instead.",
      "The useful question for AI in finance isn't 'can it pick winners.' It's 'can it read 400 pages before coffee and flag the weird footnote.' Yes. That's the job.",
      "AI won't replace your judgment. It replaces the excuse that reading everything was impossible.",
      "The best use of an AI research companion: it does the boring 90% so you can spend your energy on the judgment calls that actually need a human.",
      "If an AI ever guarantees you returns, close the tab. Real analysis deals in probabilities, not promises.",
    ],
  },
  {
    area: "what the numbers actually mean",
    takes: [
      "Revenue up 12% sounds great until you read that expenses grew 19%. Growth is not a strategy if it costs more than it brings in.",
      "A stock can be down and the company can be fine. It can also be up and the company can be on fire. The price is not the analysis.",
      "Every percentage has a base. 'Up 50%' from what? Two dollars? During what period? The context is the story.",
      "'Beat expectations' is my favorite meaningless headline. Whose expectations? The guy who lowers the bar, or the guy who raised it?",
      "Cash flow tells you what a company can actually do. Net income tells you what its accountants want you to focus on. Know the difference.",
    ],
  },
  {
    area: "portfolio honesty",
    takes: [
      "Checking your portfolio hourly is not research. It's a slot machine with extra steps.",
      "A watchlist is where hopes go to be organized. A portfolio is where they went to be tested.",
      "The question isn't 'is this stock good.' It's 'is this stock good, for me, at this price, right now, given everything else I hold.' Four extra filters. All of them matter.",
      "Everyone has a plan until they see red. Decide what you'll do when it's down 30% before it's down 30%.",
      "Your winners get all the attention. Your position sizing quietly decides whether any of it matters.",
    ],
  },
  {
    area: "do your own research, properly",
    takes: [
      "'Do your own research' doesn't mean reading five tweets. It means reading the filing, the competition, and the fine print. AI just made that a Tuesday instead of a sabbatical.",
      "The footnote is where the interesting stuff lives. Revenue recognition changes don't make headlines. They make balance sheets.",
      "Before you buy the story, check who's selling it. Insider filings are public for a reason.",
      "You don't need to know everything about a company. You need to know the three things that would change your mind. If you can't name them, you haven't researched.",
      "A thesis you can't falsify isn't a thesis. It's a vibe.",
    ],
  },
  {
    area: "plain english finance",
    takes: [
      "Finance makes everything sound harder than it is so you'll outsource the thinking. Most of it is arithmetic wearing a suit.",
      "'Dollar cost averaging' is a fancy term for 'keep buying on schedule and stop trying to time it.' You already do this with rent.",
      "A P/E ratio is just: how many years of current profits am I paying for this? Everything else is nuance on top.",
      "If you can't explain your investment thesis to a friend in three sentences, you don't have one. You have a hunch with a ticker.",
    ],
  },
];

// -- POST TYPES ------------------------------------------------------------------

const POST_TYPES = [
  "take",
  "take",
  "take", // takes are the bread and butter
  "product", // occasional Ape AI mention, kept subtle
];

// Product-flavored posts. No guarantees, no urgency, no "act now."
const PRODUCT_POSTS = [
  "Connected my brokerage to an AI research tool and asked it what I was missing. Turns out: quite a lot. That's the whole pitch, honestly.",
  "Ask Ape AI a question about your portfolio in plain English. No terminal, no jargon tax. Just answers with the numbers shown.",
  "Reading earnings reports is a job now. Ape AI reads them first and shows you the three lines that matter. You keep the judgment calls.",
  "Ape AI won't trade for you — that's not the point. It reads everything, flags the weird stuff, and lets you decide. Manual orders only, your call always.",
  "What most people miss about research: it's not finding information, it's filtering it. That's what an AI companion is actually for.",
];

// -- GENERATION ------------------------------------------------------------------

function pickRandom(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function buildTake(topic) {
  return pickRandom(topic.takes);
}

// Returns { text, topicArea } or null if nothing safe could be generated
export function generatePost(pastPosts = []) {
  const lowerPast = (pastPosts || []).map((p) => (p || "").toLowerCase());

  // Try a few times to find something not recently posted and safe.
  for (let attempt = 0; attempt < 30; attempt++) {
    const type = pickRandom(POST_TYPES);
    let text;

    if (type === "product") {
      text = pickRandom(PRODUCT_POSTS);
    } else {
      const topic = pickRandom(TOPICS);
      text = buildTake(topic);
    }

    // Guardrails: banned phrases / forbidden claims
    const check = validateText(text);
    if (!check.ok) continue; // silently try another

    // Dedup: skip if too similar to anything recently posted
    const firstSentence = text.split(/[.?!]/)[0].toLowerCase();
    const dup = lowerPast.some(
      (past) => past.includes(firstSentence) || firstSentence.includes(past.slice(0, 60))
    );
    if (dup && attempt < 25) continue; // near the end of attempts, allow reuse rather than fail

    return text;
  }
  return null;
}

export { TOPICS, POST_TYPES };
