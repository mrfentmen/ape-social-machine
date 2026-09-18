// Content guardrails for Ape AI social posts.
// Enforces BRAND-VOICE.md: banned clichés + forbidden financial claims.
// Every generated post/reply must pass validateText() before going live.

// Phrases that must never appear in a live post (case-insensitive).
const BANNED_PHRASES = [
  // clichés
  "game changer",
  "game-changer",
  "revolutionary",
  "in today's fast-paced world",
  "delve into",
  "tapestry",
  "elevate your",
  "supercharge",
  "10x your",
  "hack the market",
  // unsafe financial claims
  "guaranteed returns",
  "guaranteed profit",
  "guaranteed",
  "can't lose",
  "cant lose",
  "risk-free",
  "risk free",
  "no risk",
  "act now",
  "limited time",
  "insider tip",
  "insider info",
  "get rich",
  "sure thing",
  "always goes up",
  "never lose",
];

// Substrings that imply illegal product claims (case-insensitive).
const FORBIDDEN_CLAIM_FRAGMENTS = [
  "ape ai executes trades automatically",
  "ape ai executes your trades",
  "ape ai trades for you",
  "ape ai guarantees",
  "ape ai will make you",
  "ape ai manages your money",
  "ape ai holds your money",
  "ape ai is a broker",
  "ape ai invests for you",
  "invest with ape ai and",
];

export function validateText(text) {
  const lower = (text || "").toLowerCase();
  const hits = [];
  for (const phrase of BANNED_PHRASES) {
    if (lower.includes(phrase)) hits.push(phrase);
  }
  for (const fragment of FORBIDDEN_CLAIM_FRAGMENTS) {
    if (lower.includes(fragment)) hits.push(fragment);
  }
  return { ok: hits.length === 0, hits };
}

export function assertSafe(text) {
  const result = validateText(text);
  if (!result.ok) {
    throw new Error(
      `Guardrail violation: post contains banned phrase(s): ${result.hits.join(", ")}`
    );
  }
  return text;
}

export { BANNED_PHRASES, FORBIDDEN_CLAIM_FRAGMENTS };
