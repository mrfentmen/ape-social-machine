"""Blitz voice pools for X + Bluesky (@blitztheape persona).

Blitz = first person ape persona: punchy, irreverent, playful swagger about
doing the reading. Short lines. Plain statements. No invented figures,
no banned phrases, no guarantees, no dashes of any kind.
All lines verified with humanize_rules.validate_human before use.
"""

OPENERS = [
    "I read the footnotes so you don't have to pretend you did.",
    "I don't chase headlines. I read what the headline left out.",
    "Your broker app sells speed. I sell patience with receipts.",
    "I am just an ape with a library card and a grudge against hype.",
    "The ticker told you nothing. I read the filing instead.",
    "I asked one boring question about one boring filing. It paid.",
    "Everyone bought the story. I checked the story's math.",
    "I have no hot takes. I have cold filings and warm coffee.",
    "The chart screamed. The footnote whispered. I listen to whispers.",
    "I treat every holding like a claim that owes me proof.",
    "Market gurus shout. I read. We are not the same.",
    "I got curious about a number nobody quotes. Curiosity compounded.",
    "They posted a price target. I posted up with the 10K.",
    "I don't need luck. I need sources and a second pass.",
    "The loud take lost money quietly. I took notes.",
    "I stopped guessing and started reading. Best trade I never made.",
    "My edge is boring: I actually read the thing.",
    "I let the numbers talk first. Then I decide.",
    "The call transcript is free. Confusion is expensive. I choose free.",
    "I read filings like menus: skip the garnish, price the meal.",
    "Two tabs open: the release and the 10K. That's my whole desk.",
    "I asked what would prove me wrong. Then I went and looked.",
    "Ape see chart. Ape read filing. Ape know which one lies less.",
    "I don't worship a position. I interrogate it.",
    "The group chat traded vibes. I traded attention.",
    "I show my sources. You show your receipts. Fair trade.",
    "I checked the cash flow before I checked the comments.",
    "The release had one sentence that mattered. I found it.",
    "I keep a list of what would prove me wrong. It saves me.",
    "Reading beat reacting again today. Same result as last week.",
]

BODIES = [
    "The release said strong demand. Strong in what units? I asked. The release went quiet.",
    "I read the Q&A section first now. Analyst questions are a free map of the bear case.",
    "Buybacks moved the number. The business didn't move much. Two different stories, one ticker.",
    "Guidance is marketing with a spreadsheet attached. I read the spreadsheet part twice.",
    "A one time charge shows up every year at some companies. Recurring. Odd how that works.",
    "I checked cash from operations before I believed a single headline. Cash keeps better records than narratives.",
    "The margin note was buried three paragraphs deep. Buried things still move prices.",
    "Everyone argued about the price. I argued about the assumptions. Only one of us had evidence.",
    "The word adjusted did a lot of lifting in that release. I checked what got adjusted away.",
    "A red day is information about my temperament. I collect that data too.",
    "I wrote down why I bought. Rereading it today was uncomfortable. Uncomfortable is useful.",
    "The market priced a story. The filing described a different story. I side with paperwork.",
    "Checking the price hourly is a subscription to anxiety. I canceled that subscription.",
    "I stopped calling it a long term hold and started calling it a claim I recheck. More honest.",
    "Diversification in five versions of the same trade is concentration in a costume. I counted mine.",
    "The thesis needs everything to go perfectly for a year. That's not a thesis. That's a wish list.",
    "I asked what the number would look like without the one good quarter. Humbling exercise. Free lesson.",
    "Position sizing is the most underrated risk tool. It costs nothing and it works.",
    "The earnings release and the 10Q disagreed. Almost nobody noticed. The 10Q wins.",
    "I read the term I didn't know. Then I read why it mattered. Ten minutes. Worth more than the takes.",
    "Cost basis is not physics. The market never once asked what I paid. I got over it.",
    "The upgrade arrived near the high. Momentum wearing a suit. I checked the math anyway.",
    "A loss I planned for is tuition. A loss I didn't plan for is a leak. I patch leaks.",
    "Every app makes buying one tap. None makes reviewing one tap. Notice the incentive.",
    "I audit my own history now. The investor who writes reasons down can't lie to himself later.",
    "Volatility is not risk. Permanent loss is risk. The difference sells a lot of products.",
    "The narrative changes weekly. Unit economics change yearly. I bet on the slower clock.",
    "I asked which number nobody was quoting. Turns out it was the one that decided things.",
    "Seasonality gets cited like physics. It's closer to trivia. I stopped paying for trivia.",
    "A green month tests discipline. A red month tests the thesis. Both exams matter.",
    "The smartest take I read was written by someone with opposite exposure. I keep that in mind.",
    "I read the whole Q&A. Management answered everything except the thing I asked. That was the answer.",
    "Backtests don't pay for groceries. Boring consistency might. I shop accordingly.",
    "Historical parallels are astrology with spreadsheets. I checked the footnote instead.",
    "The company that can't explain its own numbers in one sentence is asking for trust on credit. No thanks.",
    "I keep my receipts: filings, dates, reasons. Confidence without homework is decoration.",
    "The footnote is where they legally had to tell you. I read it like a favor. It is one.",
    "Noise has an hourly cadence. News has a quarterly one. Confusing them is expensive. I stopped.",
    "I would rather be slow and right than fast and confident. The receipts prefer it too.",
    "A thesis without a falsification condition is a tattoo. Mine are in pencil. Erasable.",
    "Nobody grades thoroughness. The market grades results. I still do the reading. Results improved.",
    "I found the precedent for an unprecedented quarter in an older filing. Research finds things.",
]

CLOSERS = [
    "Ask the boring question. It pays best.",
    "Sources or silence. Pick one.",
    "I read. You decide. Fair deal.",
    "Ape did the homework. Ape sleeps fine.",
    "Check the cash. Then talk.",
    "The footnote called. It matters.",
    "Bananas are cheap. Excuses aren't.",
    "Read the release. Then decide.",
    "Keep your reasons where you can reread them.",
    "Slow reads, fast decisions.",
    "Numbers first. Narrative second.",
    "The filing is free. The regret isn't.",
    "Less vibes. More filings.",
    "Verify once. Panic less.",
    "Ask what proves you wrong. Then look.",
    "Ape AI reads it. You decide. AskApe.com.",
    "AskApe.com. Bring the skepticism.",
    "One filing read beats ten takes watched.",
    "Sourced or silent. That's the bar.",
    "The judgment stays yours. The homework doesn't.",
    "Fewer tabs. More answers.",
    "Research like you mean it.",
    "Check what changed. Then check it again.",
    "Write the claim down. Revisit it.",
    "Plain answers, sources attached. AskApe.com.",
]

# ------------------------------------------------------------------ hashtags
# Blitz tag pools for X + Bluesky. Brand tag first, always included when any
# tag fits. All letters only (humanize_rules passes them), no figures,
# no banned words. Keep total tag count < 5 (guardrails spam rule).
BRAND_TAGS = ["#AskApe"]

DISCOVERY_TAGS_X = [
    "#FinTwit", "#StockMarket", "#Earnings", "#Research", "#Investing",
    "#Markets", "#DD", "#Filings", "#Trading", "#AI",
]

DISCOVERY_TAGS_BSKY = [
    "#investing", "#stocks", "#finance", "#markets", "#earnings",
    "#research", "#AI", "#stockmarket",
]


def pick_tags(rng, platform: str, budget_chars: int) -> str:
    """Deterministic tag line for a post: brand tag FIRST, then discovery
    tags up to 3 total. Shrinks to fewer tags if the char budget is tight.
    Returns '' if even the brand tag doesn't fit. rng must be a
    random.Random (seeded per post for stable reruns).
    """
    disc = DISCOVERY_TAGS_X if platform == "x" else DISCOVERY_TAGS_BSKY
    brand = BRAND_TAGS[0]
    if len(brand) > budget_chars:
        return ""
    chosen = [brand]
    rest = list(disc)
    rng.shuffle(rest)
    for tag in rest:
        if len(chosen) >= 3:
            break
        line = " ".join(chosen + [tag])
        if len(line) <= budget_chars:
            chosen.append(tag)
    return " ".join(chosen)
