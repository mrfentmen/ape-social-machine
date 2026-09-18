"""LinkedIn pools: skill voice per skill.txt (company page, discussion-driven).

Framework: Hook, what happened, the numbers, why it matters, what most people
miss, how Ape AI helps, CTA. Intelligent, credible, insight-heavy. No mascot
narrator. No invented figures. No dashes of any kind.
All lines verified with humanize_rules.validate_human before use.
"""

OPENERS = [
    "The most useful investing skill of the next decade will be knowing what to ignore.",
    "Every quarter, companies publish the answers. Most readers never find the questions.",
    "Between the headline and the decision, there is a gap. Most portfolios live in that gap.",
    "A portfolio review is only as honest as the tools that feed it.",
    "The market is unusually good at telling people what happened and unusually bad at telling them why.",
    "The professionals' edge was never secrecy. It was throughput, and throughput is now buyable.",
    "Most investing mistakes are made in the ten minutes after a headline is read.",
    "Earnings season is a vocabulary test that nobody signed up for, taken at market speed.",
    "Access to markets got solved a decade ago. Access to understanding is the open problem.",
    "The interesting question in fintech right now is not what AI can generate. It is what AI can verify.",
    "There is a quiet difference between feeling informed and being informed. Portfolios can tell.",
    "The most expensive part of retail investing is not fees. It is unstructured confidence.",
    "Every position in a portfolio is a claim about the world. Most claims were never written down.",
    "Financial literacy campaigns failed for a simple reason: they teach vocabulary when no decision is pending.",
    "The industry keeps selling conviction. What actually helps is better friction.",
    "Information is abundant. Judgment is scarce. The entire product gap lives between them.",
    "The filing was written by professionals, for professionals. Pretending otherwise is how mistakes happen.",
    "Trust in AI financial tools will be earned through failure behavior, not accuracy claims.",
    "The vocabulary of earnings releases is a status system, and it excludes people who could otherwise contribute.",
    "A portfolio drifts one unreviewed quarter at a time. Drift is a default, not a decision.",
]

MID = [
    "Here is what changed:",
    "Consider the mechanism:",
    "What the numbers say:",
    "Why it matters:",
    "What most people miss:",
    "The practical implication:",
    "The uncomfortable part:",
    "The evidence points one way:",
]

BODIES = [
    "A headline reports the number. The release explains the number. The footnote qualifies the explanation. Most readers stop at step one, and the entire difference between reacting and deciding lives in steps two and three.",
    "Companies disclose an enormous amount. The disclosures are engineered for legal precision rather than reader speed. A research layer does not change what is disclosed. It changes who can afford to read it.",
    "Earnings season rewards one specific skill: telling, within an hour, whether an update actually touched your thesis. That triage is teachable, and it is mostly tooling. Speed of reaction is not the skill. Speed of relevance detection is.",
    "Brokerage connectivity is usually framed as convenience. It is more accurate to call it context. Without holdings data, research is generic. With it, the question shifts from what happened in the market to what happened to what you actually own.",
    "The professional retail divide is not about intelligence or effort. It is infrastructure. Professionals have aggregation, tagging, and context built into their tools. Retail has open tabs. Closing that gap is the most valuable work fintech can do.",
    "Portfolio honesty is a discipline, and like most disciplines it fails quietly. Holdings spread across apps, cost basis in one place, notes in another. The friction guarantees the review happens less. Consolidation is what makes the discipline possible.",
    "Skepticism of AI in investing is healthy. The useful version asks whether the tool cites sources, distinguishes fact from estimate, and says the filing does not say when the data is missing. Products that clear that bar reduce risk. Products that do not are faster hype.",
    "The best research habit costs nothing: for every position, write the sentence that would change your mind. Then, when a headline arrives, check it against that sentence. This turns breaking news from a trigger into a test.",
    "Position concentration rarely feels like a decision. It accumulates through inertia: winners left to run, adds made in familiar names, nothing deliberately rebalanced. Surfacing drift is not hand holding. It is the difference between a strategy and a habit with equity exposure.",
    "Most retail research time is spent assembling context that already exists: what the company does, what the segment names mean, which numbers the market tracks. That assembly is compressible. The judgment, whether the update changes the thesis, is not, and that division of labor is the whole point of a research companion.",
    "The vocabulary gap deserves more attention than it gets. Impairment, revision to provision, change in fair value: each is one plain English sentence, and each carries a different implication for a thesis. Translating terminology is not simplifying investing. It is removing a gate that never held anything up.",
    "The Q&A section of an earnings call is the closest thing markets have to cross examination. Analyst questions reveal the consensus bear case. Evasive answers reveal where management feels thin. Summarizing those exchanges by theme does more for research quality than any new chart.",
    "There are two versions of AI in finance. One generates confident output with no sources. The other shows its work: the claim, the source, and the qualifier, all visible. The first is a liability wearing a product badge. The second is what research assistance actually means.",
    "Every portfolio has a shadow portfolio: the trades considered and skipped. Reviewing skipped ideas reveals whether a process filters well or just filters familiar. Visibility into that record is where improvement actually starts.",
    "The most durable products in fintech do one boring thing reliably: they shorten the distance between a question and a sourced answer. Scores, signals, and predictions age badly because they inherit the market's uncertainty while pretending not to.",
    "Financial content is optimized for the moment after reading: the reaction. Research is optimized for the moment after that: the decision. The two genres look identical in a feed and behave nothing alike over a year. Distinguishing them is the first skill worth building.",
    "Millions of people will pick stocks regardless of what the industry thinks they should do. They deserve better inputs than a notification and a vibe. Meeting people where they actually are beats correcting them from where they should be.",
    "A quarterly report is a transcript of what management wants remembered. Reading it that way changes the experience entirely: what is emphasized, what is de emphasized, and what appears for the first time all become signals instead of background.",
    "The annual report has a structure that rewards patience: business description, risk factors, then numbers. Most readers invert it. Reading in order, even once, explains why the numbers look the way they do.",
    "Nothing in a filing changes because a chart moved. The causation only runs one way, and keeping that direction straight is most of the discipline.",
]

CTAS = [
    "What does your research process look like when the week is busy? The honest answers are the useful ones.",
    "Which section of a filing do you read first, and why? The comment section tends to teach more than the post.",
    "If you could ask one plain English question about any company and get a sourced answer, what would it be?",
    "What is the first thing you check after the headline? Add yours below. The list keeps improving.",
    "How do you currently separate signal from noise during earnings week? Genuinely curious what process looks like.",
    "Where does your research time actually go? Most people have never measured it. Worth doing once.",
    "What convinced you to trust, or distrust, an AI research tool? The answers shape what gets built.",
    "If your research process had a weekly ritual, what would it be? Collecting the good ones.",
    "What term have you had to look up mid filing? Someone else needs that answer too. Drop it below.",
    "If this is the kind of research you want more of, that is the product: AskApe.com.",
]
