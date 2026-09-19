"""IG caption pools, batch 2.

Extra contexts and insights for every theme in ig_pools.py. New lines only:
nothing here repeats a line from the first pool file. Loaded automatically by
ig_pools.py, which extends each theme with these lines so the caption generator
has roughly three times the hook/context/insight combinations it had before.

Rules for every line: dash free, American spelling, no invented figures, no
promises or advice, straight apostrophes only.
"""

EXTRA = {
    "AI stock research": {
        "contexts": [
            "The way most people use these tools is backwards. They ask for a prediction and get a confident paragraph they cannot check. Ask for an explanation instead and every answer points back to something you can open and read.",
            "Consider how long it takes to answer a simple question today. What changed at this company, when did it change, and did management say anything about it. Three answers, three different places, and the clock keeps running while the price moves.",
        ],
        "insights": [
            "Compare the question you asked five years ago with the one you ask now. If it is still just which stock is going up, no tool will help you, because that is not a question with an answer.",
            "Read the primary document once a week, even when a tool summarizes it. Summaries are useful for finding the paragraph, and the paragraph is where the detail that matters usually hides.",
            "Notice how often the reason a stock moved is boring. A guidance change, a contract, a filing. The dramatic explanations travel further and are usually the wrong ones.",
            "Build one page for each name you hold. What it sells, how it makes money, who it competes with, and what would change the story. A copilot can help you fill it, and the filling is the point.",
            "Treat every answer as a starting point you still have to verify. The skill being learned is not how to ask, it is how to tell a supported claim from a confident one.",
        ],
    },
    "Beginners": {
        "contexts": [
            "The practical version of starting looks boring. Pick a small amount you are comfortable not touching, buy something broad, and spend the first month reading instead of trading. The reading is the investment.",
            "Beginner questions get better answers when you notice who is answering. Someone selling a course and someone explaining a filing have different reasons to speak, and both sound helpful at first.",
        ],
        "insights": [
            "Learn the difference between a company and a ticker early. One is a business with customers and costs, the other is a label that moves on news. New investors lose money on the label and think they lost it on the business.",
            "Keep a beginner journal. What you bought, why, and what you expected to happen. Revisit it in a month. Almost nobody does this and almost everybody should.",
            "Do not confuse activity with progress. A quiet week where you read one filing is worth more than five trades you cannot explain.",
            "Know what you are paying for. Commissions, spreads and expense ratios are small numbers that compound against you quietly for years.",
            "Ask why the person giving advice would give it to you for free. Some are generous, some are selling, and the difference is worth knowing before you act on it.",
        ],
    },
    "Earnings and filings": {
        "contexts": [
            "Earnings season compresses a lot of information into a few weeks. The people who find it manageable are not reading more, they are reading the same few sections on a schedule.",
            "A filing is written to be accurate, not friendly. Telling yourself that in advance removes a lot of the frustration when the sentences are long and the answer is buried in a footnote.",
        ],
        "insights": [
            "Read the risk section of a filing once, properly. It is the least exciting part and the one that most often explains what goes wrong later.",
            "Compare what management said last quarter with what they said this quarter. Changes in wording are cheaper to spot than changes in numbers, and often arrive first.",
            "Watch the difference between revenue and profit in one report. A company can grow sales and shrink profit in the same quarter, and that combination is what people miss.",
            "Read the notes before the press release summary. The summary is written to be read quickly, and the notes are where the qualifications usually live.",
            "Keep your own one line summary of each report you read. After a few quarters you have a record of what actually changed, instead of a vague memory of a good or bad day.",
        ],
    },
    "Why stocks move": {
        "contexts": [
            "Big moves are usually a crowd meeting a surprise. The surprise is in the news, the crowd is in the positioning, and the price is the record of both meeting at once.",
            "Ask what would have to be true for the move to make sense. If nothing plausible fits, the honest answer is often that you do not know yet, and waiting is a position.",
        ],
        "insights": [
            "Not every move has a story worth chasing. Sometimes a large holder sells, sometimes an index rebalances. Those reasons are real and they are not about the business.",
            "Check whether the whole sector moved or just your name. One tells you about an industry, the other tells you about a company, and confusing them leads to the wrong conclusion.",
            "Notice how often the explanation arrives after the price. The move happens, then the headline explains it, and the explanation is written to fit the chart.",
            "Write down the reason on the day. A week later you will remember the price and not the cause, and the cause is the part you can learn from.",
            "Understand that price is an opinion formed by the last person willing to trade. It is useful information about demand and it is not a verdict on the business.",
        ],
    },
    "Watchlists and routines": {
        "contexts": [
            "A watchlist is only useful if it has a reason next to each name. Without one it becomes a list of things that caught your eye once, which is closer to a scrapbook.",
            "Morning routines get the attention, but the evening review is where the value sits. Markets are noisy in the morning and quieter afterwards, and quieter is when people think clearly.",
        ],
        "insights": [
            "Keep your list short enough that you can explain every name on it. A very long list is usually a sign that nothing on it has been researched.",
            "Review your list on a fixed schedule rather than when you feel like it. The schedule is what makes the list a process instead of a mood.",
            "Remove names that no longer belong. A watchlist that only grows slowly turns into a source of decisions you should not be making.",
            "Write one sentence about what you are waiting for on each name. A list of triggers is a plan, and a list of tickers is just a list.",
            "Do the boring part at the same time every day. Consistency is what turns a habit into a record you can actually learn from.",
        ],
    },
    "Risk and psychology": {
        "contexts": [
            "Most bad decisions are made in the gap between a feeling and an action. Widening that gap by a few minutes is a practical skill, and it is trainable.",
            "Losses feel larger than gains of the same size, and that is not a character flaw, it is how most people are built. Knowing it in advance is the start of handling it.",
        ],
        "insights": [
            "Size is the decision you control most directly. Being right about a direction and wrong about size is the same as being wrong.",
            "Notice which positions you check most often. Frequent checking usually tracks anxiety rather than information, and it quietly encourages you to act.",
            "Expect a losing streak eventually. A plan that only works while everything goes well is not a plan, it is a mood.",
            "Separate the decision from the outcome. A good decision can lose money and a careless one can make money, and only one of those is repeatable.",
            "Decide what would make you change your mind before you need to. Written in advance, it is analysis. Decided in the moment, it is usually just discomfort talking.",
        ],
    },
    "Instruments": {
        "contexts": [
            "Different products solve different problems. Someone saving for a decade and someone learning how options behave need different tools, and using one for the other job is where most confusion starts.",
            "Before comparing two funds, compare what they hold. Two products with similar names can own very different things, and the name is the last place to look.",
        ],
        "insights": [
            "Understand what happens to your instrument if the market goes nowhere for a year. Some products are built to be flat, and knowing that in advance prevents a lot of frustration.",
            "Look at what an instrument owns underneath. A basket is a bundle of decisions someone else made, and it is worth knowing which ones you are accepting.",
            "Read how the thing is priced before you trade it. Products with wide spreads cost you on the way in and on the way out, quietly.",
            "Match the holding period to the instrument. Short term tools held long term and long term tools traded short term are two of the most common quiet mistakes.",
            "Know what you are actually exposed to. A familiar ticker can hold something unfamiliar inside it, and the label rarely tells you.",
        ],
    },
    "Noise and understanding": {
        "contexts": [
            "Most of what arrives in a day is repetition. The same story, rewritten by different outlets, with the urgency turned up because urgency is what gets opened.",
            "Cutting sources is harder than adding them. Every feed you joined was useful once, and nobody sends a reminder telling you it stopped being useful.",
        ],
        "insights": [
            "Ask what you would do differently if you had not read something. If the answer is nothing, it was entertainment wearing the costume of information.",
            "Notice how a story grows. A single filing becomes a headline, the headline becomes a take, and the take becomes a reason people buy without reading the filing.",
            "Keep one source you disagree with. Agreement feels good and teaches little, and the disagreement is where your reasoning gets tested.",
            "Choose what to ignore deliberately. Attention is the only input you fully control, and most of the timeline is designed to take it.",
            "Judge your understanding by what you can explain without looking it up. If the words only work while the article is open, they were never yours.",
        ],
    },
}
