"""SEO caption pools for @blitztheape Instagram reels.

Same convention as blitz_pools.py / pools.py / skill_li_pools.py: every line is
DASH FREE (BRAND-VOICE.md humanized rules), evergreen, fact-safe, no invented
figures, no advice, no returns language. Each caption is assembled from one
theme so the paragraphs stay on topic:

    HOOK -> CONTEXT -> INSIGHT -> [EXTRA] -> CTA_BLOCK -> CTA -> DISCLAIMER -> TAGS

Themes exist so an assembled caption never jumps subjects. Every pool line is
checked with humanize_rules.validate_human by the generator before anything is
written out.

Rules baked into the line pools:
- no dashes of any kind, no spelled out numbers above ten, American spelling
- no banned phrases (see generate_ig_captions.BANNED)
- no prices, no percent moves, no performance claims of any kind
"""

# --------------------------------------------------------------- shared pools

# What Ask Ape AI is, in different words. Every line names the URL and states
# what the tool does NOT do, because that framing is required on every post.
CTA_BLOCK = [
    "This is the job Ask Ape AI was built for. It is an AI research copilot for retail investors: ask a question in plain English and get a plain English answer drawn from filings, earnings and market news. Start at http://AskApe.com. It does not execute trades, does not give financial advice and does not promise returns.",
    "That is where Ask Ape AI helps. http://AskApe.com is a conversational research copilot, built to explain companies, earnings and price moves without the jargon wall. It is an educational tool. No trade execution, no advice, no promised outcomes.",
    "Ask Ape AI exists for this exact gap. http://AskApe.com reads the filings, the earnings release and the news, then answers your question the way a patient person would. It never places a trade, never recommends a position and never promises a return.",
    "This is what Ask Ape AI was designed to do. Head to http://AskApe.com, ask your question in everyday language and get context instead of a sales pitch. Educational research only: no execution, no personal advice, no guarantees.",
    "That question is exactly what Ask Ape AI answers. http://AskApe.com is an AI copilot for market research and education, not a broker and not a signal service. Ask it what a company does, why a stock moved, what an earnings report actually said.",
    "This is why Ask Ape AI was built. At http://AskApe.com you can ask about a company, an earnings report or a price move and get a clear, sourced explanation in seconds. It does not trade for you, does not advise you and does not promise anything.",
    "Ask Ape AI is the answer to that friction. http://AskApe.com turns a plain English question into a plain English explanation of the filings, the numbers and the news. Educational tool only: no trade execution, no advice, no promised returns.",
    "That is the workflow Ask Ape AI was designed around. http://AskApe.com lets you ask what changed, why it matters and what the market is reacting to, and answers in language a normal person can use. It does not execute trades and does not give financial advice.",
    "This is the part Ask Ape AI shortens. http://AskApe.com is a research copilot for everyday investors: ask about a business, an earnings call or a sudden price move and get a straight answer. No trade execution, no advice, no promises about outcomes.",
    "Ask Ape AI was built for exactly this. http://AskApe.com answers market questions in plain English using filings, earnings and news, so research stops being a wall of tabs. It is educational only and it never trades, advises or promises.",
    "That gap is what Ask Ape AI closes. Go to http://AskApe.com, ask your question the way you would ask a friend, and get an explanation grounded in the actual documents. No execution, no recommendations, no promises.",
    "This is where Ask Ape AI fits. http://AskApe.com is a conversational layer over earnings, filings and market news, built for people who want understanding rather than alerts. It does not place trades and it does not give advice.",
    "Ask Ape AI is the tool for that question. http://AskApe.com explains a company, a filing or a price move in everyday language, backed by sources you can check. Educational research only: no trades, no advice, no guaranteed anything.",
    "That is what Ask Ape AI is for. http://AskApe.com takes the question you actually have and answers it with the numbers and the context behind the headline. It does not execute trades, does not advise and does not promise returns.",
    "This is exactly where Ask Ape AI helps. http://AskApe.com is an AI copilot for market research and education, so you can ask about a business, an earnings report or a strange price move and get clarity fast. No execution, no advice, no promises.",
    "Ask Ape AI exists to remove that step. http://AskApe.com answers plain English questions about companies, earnings and market moves, which is most of what research actually is. It does not trade, does not advise and does not promise outcomes.",
    "This is the job Ask Ape AI does. http://AskApe.com reads the release, the filing and the news, then gives you the short version you can use. Educational only: no trade execution, no personal advice, no promised returns.",
    "Ask Ape AI was made for people who want the why, not just the ticker. Start at http://AskApe.com with any question about a company, an earnings report or a price move. It does not execute trades and it does not give financial advice.",
    "That is the gap Ask Ape AI fills. http://AskApe.com is a research copilot you talk to, so the answer arrives in seconds and in words you can repeat out loud. No execution, no advice, no promises of any kind.",
    "This is what Ask Ape AI was built to make normal. http://AskApe.com turns a question about a business, a filing or a price move into a clear answer with the reasoning attached. Educational tool only: no trades, no advice, no guaranteed results.",
]

CTA = [
    "Start with one question. The habit builds from there.",
    "Ask the boring question first. It teaches the most.",
    "Write the answer down. That is how understanding compounds.",
    "Pick one company this week and learn what it actually sells.",
    "Stop guessing at the why. Go read the why.",
    "One question a day beats one hour a month.",
    "Curiosity is a skill. It has reps.",
    "Slow the decision, speed the research.",
    "Learn the words, then the numbers, then the news.",
    "Ask better questions and the market gets less confusing.",
    "Come back tomorrow. Same place, same five minute habit.",
    "Read one filing this week. It changes how news sounds.",
    "The app can wait. The understanding cannot.",
    "Trade less on impulse, research more on purpose.",
    "Keep a note of what you did not know. It is a map.",
    "Understanding is the only edge that stays with you.",
    "Start small, stay curious, keep receipts.",
]

DISCLAIMER = [
    "For educational purposes only. Not financial advice.",
    "Educational content only. Not investment advice.",
    "This is general education, not personalized advice.",
    "For education only. Not financial advice.",
    "Educational purposes only. Nothing here is advice.",
]

# Discovery tags rotated three at a time. #AskApe and #AskApeAI are always first.
TAG_BRAND = ["#AskApe", "#AskApeAI"]
TAG_POOL = [
    "#AIInvesting", "#AIFinance", "#AIStockResearch", "#AIInvestingTools",
    "#AITrading", "#StockMarket", "#StockMarketNews", "#StockMarketEducation",
    "#StockMarketForBeginners", "#StockAnalysis", "#StockTrading",
    "#Investing", "#Investing101", "#InvestingForBeginners", "#InvestingBasics",
    "#InvestingTips", "#LearnToInvest", "#FinancialEducation",
    "#FinancialLiteracy", "#FinancialFreedom", "#RetailInvestor",
    "#MarketNews", "#MarketRoutine", "#DayTrading", "#SwingTrading",
    "#TradingEducation", "#TradingPsychology", "#RiskManagement",
    "#PortfolioManagement", "#Dividends", "#ETFs", "#IndexFunds",
    "#PassiveIncome", "#MoneyTips", "#MoneyMindset", "#WealthBuilding",
    "#ChartPatterns", "#Premarket", "#Earnings", "#Volatility",
    "#NYSE", "#WallStreet", "#NYCInvestor", "#AxelBlitzBeaumont",
    "#ResearchHabits",
]

# --------------------------------------------------------------- themes

THEMES = [
    {
        "name": "AI stock research",
        "focus": "AI stock research, AI investing, research copilot",
        "hooks": [
            "Most retail investors do not lose money because they are careless. They lose because they are buried. Too many tabs, too many alerts, too many opinions, and no clear answer to the one question that matters today.",
            "AI stock research is not about letting a machine pick stocks. It is about closing the distance between the question in your head and a clear answer you can actually use.",
            "There is a version of investing research where you open a chart, ask why, and know the reason in seconds. That version is now available to anyone with a phone.",
            "The research problem in retail investing was never a shortage of information. It is a shortage of translation between what companies publish and what normal people can understand.",
            "Every investor eventually asks the same question. Why did this stock move. The difference between people who learn from that question and people who panic is how fast they can find the real answer.",
            "An AI research copilot will not make you a better investor on its own. It makes the reading fast enough that you actually do it, and that is what changes the math.",
            "The question is not whether AI belongs in investing research. It is whether you want to spend your evening opening documents or understanding them.",
        ],
        "contexts": [
            "Think about the last time a stock you own moved sharply. If you found the reason in minutes, you had an edge. If you spent the afternoon scrolling and still could not explain it, the information existed the whole time and you simply could not reach it.",
            "The old workflow is a scavenger hunt. A screener shows a name, a browser tab shows a headline, a forum shows an opinion, and none of them explain the business behind the ticker. That gap is where most confusion lives.",
            "Market data has never been cheaper and understanding has never been more expensive, because the data arrives as a firehose and the explanations arrive as ads.",
            "Think about what a research copilot is actually doing. It is not thinking for you and it is not forecasting. It compresses documents, finds the relevant line and explains it in the language you use. The judgment still belongs to the person clicking.",
        ],
        "insights": [
            "In practice this looks like one question instead of several searches. What does this company do, what changed, and why did the price react. Answer those three and you understand more than most of the timeline does, because most of the timeline stopped at the headline.",
            "The trick is to separate three things that get blended together. The business, which changes slowly. The news, which changes daily. And the price, which changes constantly and reacts to both. Confusing the three is how people end up holding a stock for a reason that stopped being true months ago.",
            "Research has a shape. Ask what the company sells, then whether the numbers are moving in the right direction, then what management said about the next 12 months. Those three layers cover most of what a retail investor actually needs, and each one takes minutes once you know where to look.",
            "Clarity beats conviction in this game. A person who understands a boring business can sit through a bad week. A person who bought a story cannot, because they have nothing to measure the noise against.",
            "Watch for the trap of outsourcing opinion. A tool that answers why did this move is useful. A tool that tells you what to buy is a different product with a different incentive, and the second one is much easier to sell.",
        ],
        "extras": [
            "One more thing worth building: a written reason for every position you hold. Not a long one. A sentence. Rereading those sentences on a red morning is the fastest way to find out which of your reasons were real.",
            "Speed of comprehension is the whole advantage. The market will always have more information than you can read, so the only realistic goal is understanding the slice that touches your portfolio, and understanding it before your emotions get a vote.",
            "One pattern worth noticing: the stocks that confuse you most are usually the ones you have not researched yet. Confusion is a research queue, not a verdict.",
            "And know what a copilot is good at. It is excellent at compressing documents and explaining what changed. It is not a forecast, and treating it like one turns a research tool back into a betting slip.",
            "Keep a short list of questions you cannot answer yet. Every one of them is a small gap in your understanding, and gaps are where money leaks out quietly.",
            "Finally, check the source. Any answer worth acting on points back to a filing, a transcript or a report you can open yourself. Understanding you cannot verify is just confidence.",
        ],
    },
    {
        "name": "Beginners",
        "focus": "stock market for beginners, learn to invest, investing basics",
        "hooks": [
            "If you are new to the stock market, the hardest part is not picking a stock. It is deciding which of the endless opinions you are supposed to take seriously.",
            "Nobody is born understanding the stock market. It is a vocabulary, a set of habits and a pile of paperwork. That is all it ever was.",
            "Starting to invest is mostly a translation problem. The industry writes for people who already know the words, and then wonders why beginners feel behind.",
            "The first year of investing is not about returns. It is about building a process you can repeat without needing motivation.",
            "Beginner investors do not need a hot idea. They need a handful of words, a weekly habit and a clear idea of what would prove them wrong.",
            "The first stock you buy will teach you more than the first ten articles you read about buying stocks. Do the small version early.",
            "Everyone starts by wanting a good pick. The people who last start by wanting a good process.",
        ],
        "contexts": [
            "Here is the honest version of how to start. Learn the vocabulary before the tickers. Share, earnings, guidance, dividend, market cap, index, expense ratio. If a word shows up in a headline and you cannot define it, that is today's homework.",
            "A lot of beginner advice skips straight to stock picking, which is like teaching someone to drive by handing them a map of a city they have never seen. The basics are boring and they are the reason some people last decades while others quit after one bad month.",
            "The gap is not intelligence. It is exposure. People who grew up around markets absorbed the language by accident, and everyone else is expected to catch up in their spare time.",
            "New investors are told to think long term, which is advice about patience given to people who have not built the habit that makes patience possible. The habit comes first, and it is small.",
        ],
        "insights": [
            "Start with what you own. A share is a slice of a business. A chart is a record of what people paid for that slice. Reread that sentence before every trade, because most beginner mistakes come from forgetting which one they bought.",
            "Write the reason before you buy, not after. If you cannot explain it in one sentence, you do not have a thesis, you have a feeling, and feelings do not survive contact with a red week.",
            "Expect to be wrong and plan for it. Risk management is the unglamorous skill that separates people who stay in the market from people who blow up once and quit forever.",
            "Learn in small amounts. Small positions, small stakes, real lessons. Nobody learns anything useful from a practice portfolio they never cared about.",
            "Understand what you own before you increase what you own. Adding to a position you cannot explain is not conviction, it is a larger version of a guess.",
        ],
        "extras": [
            "And keep a notebook. What you bought, why, what you expected, what happened. After a few months that notebook will teach you more about your own behavior than any course will.",
            "One more beginner rule that pays off quietly: never research in a hurry. Decisions made in a rush are guesses wearing the costume of a plan.",
            "One habit worth more than any indicator: read the company description in the filing. One page, plain language, and suddenly the ticker has a business behind it.",
            "And ignore anyone who makes this sound effortless. The people who last made the learning boring and repeatable instead of exciting and occasional.",
            "Write your questions down as they arrive. A list of things you do not understand yet is the most useful document a new investor owns.",
            "Finally, protect the habit. 10 minutes a day for a year teaches more than one intense weekend you never repeat.",
        ],
    },
    {
        "name": "Earnings and filings",
        "focus": "earnings report explained, how to read a filing",
        "hooks": [
            "Earnings season is where retail investors get their worst surprises, and it is almost always because they read the headline instead of the report.",
            "A company publishes more truth in one quarterly filing than it publishes in a year of marketing, and almost nobody reads it.",
            "The headline tells you whether a company beat or missed. It almost never tells you whether the business is getting better or worse, which is the only thing that matters over time.",
            "Most earnings reactions make sense once you read three paragraphs. The problem is that nobody reads three paragraphs when a headline is shouting.",
            "Filing season is a vocabulary test with financial consequences. Learn five terms and the fog lifts considerably.",
            "Two companies can report the same headline number and deserve completely different reactions. The difference is always further down the page.",
            "A quarterly release is a marketing document with audited neighbors. Both parts matter, and only one of them is on the front page.",
        ],
        "contexts": [
            "Revenue, earnings per share, guidance, margins, and the outlook for next quarter. That is the story most of the time. The release leads with the flattering version, and the fine print carries the part that decides how the stock behaves for the following month.",
            "Here is the part people skip. A company can beat on earnings and still fall sharply, because guidance was soft. It can miss and still rise, because the miss was already expected and the outlook improved. Markets price expectations, not report cards.",
            "Every filing has a section where management is legally required to spell out the risks. It is the least read section in finance and the most useful one for anyone trying to avoid a surprise.",
            "Reading a filing gets easier when you stop trying to read all of it. Numbers first, then the outlook, then the risk section. That order matches the order the market actually cares about.",
        ],
        "insights": [
            "Ask three questions after any report. What did they say about the next quarter. What changed in the actual business. And how did the stock react compared to those first two answers. If the reaction does not match the fundamentals, you are watching positioning, not news.",
            "Watch the difference between cash and accounting. A company can report a profit while its cash flow shrinks, and that gap is usually described in language designed to be skimmed past.",
            "Guidance is a forecast, not a promise. Management is telling you what they expect, which is useful context and useless certainty. Treat it as a claim to be tracked, not a number to be trusted.",
            "One and done charges have a habit of showing up every year at certain companies. When something described as unusual happens on a schedule, it is worth asking what the numbers look like without it.",
            "The most useful habit in earnings season is writing your expectation down before the report. A company that beats your own bar is different information than one that beats somebody else's.",
        ],
        "extras": [
            "If you only ever read one section, read the questions analysts ask on the call. Their questions map out the bear case for free, because that is what they are paid to probe.",
            "And compare the release to the filing. When the two narratives disagree even slightly, the filing is the version with legal weight behind it.",
            "Watch what management does, not only what it says. Buybacks, insider activity and capital spending show what the people closest to the numbers actually believe.",
            "Read two quarters, not one. A single report can flatter a business that is quietly getting worse, while a pair of them makes the direction obvious.",
            "Keep a short note per report. What changed, what surprised you, what you will watch next. That file becomes your own research desk.",
            "Finally, do not confuse a good company with a good entry. Both matter and they are separate questions.",
        ],
    },
    {
        "name": "Why stocks move",
        "focus": "why a stock moved, market news explained, catalysts",
        "hooks": [
            "Why did that stock move today. It is the most common question in retail investing and most answers online are either guesses or sales pitches.",
            "A price is an argument between buyers and sellers. Most days the argument is boring, and a few days a year it decides how you feel about your entire portfolio.",
            "Most price moves trace back to a short list of causes. Learn the list and the daily noise stops feeling random.",
            "The market never moves because something is obvious. It moves because expectations changed, and expectations are usually the thing nobody wrote down.",
            "If you cannot explain why a stock moved, the honest answer is that you do not know yet. That is fine. What is not fine is inventing a reason to justify a decision.",
            "A stock can fall on good news and rise on bad news. Neither is a mystery once you know what the market was already expecting.",
            "Most people ask what happened. The better question is what changed, and the two are not always the same answer.",
        ],
        "contexts": [
            "Company news, macro news, sector news and positioning. Those are the buckets. Earnings and guidance belong to the first, interest rates and inflation data to the second, one big name repricing a whole group to the third, and a crowded trade unwinding to the fourth.",
            "Thin trading exaggerates everything. A modest amount of money moves a name further before the regular session than it would at midday, which is why premarket spikes so often fade once real liquidity shows up.",
            "Timelines reward a story and markets reward a cause. The two are related but they are not the same thing, and mixing them up is how people build a thesis out of vibes.",
            "The first reaction to news is usually about positioning and the second is about substance. Watching the second is slower, less exciting and far more informative about the business.",
        ],
        "insights": [
            "The habit that helps is asking why before asking how much. If a move traces back to a genuine change in the business, that is one conversation. If it traces back to a single headline and a wave of attention, that is a completely different one.",
            "Tag the move to one of the buckets and you already understand more than the comment section. If you cannot tag it, say so out loud, because a reason you invented is worse than no reason at all.",
            "Not every red candle means something broke. Sometimes a stock falls because a large holder trimmed a position, and that tells you nothing about the business or its future.",
            "Look at how the stock behaves after the news, not just on the day. A move that holds over the following weeks was probably information. A move that fades was probably attention.",
            "Separate the move from the reason. A chart tells you what happened, a filing tells you why, and only one of them can be researched before the market decides.",
        ],
        "extras": [
            "One habit that builds real skill: log the reason for a big move, then revisit it a week later. Your first read will be wrong about a third of the time, and knowing that is worth more than being confident.",
            "And watch the whole sector, not just your name. Single stocks rarely move alone, and the group tells you whether you are looking at a company story or a market story.",
            "Notice what the stock does over the following week, not just the hour. First reactions are often the loudest and least accurate read of the news.",
            "Treat unexplained moves as unanswered questions rather than invitations. Nothing forces you to act on a candle you cannot explain.",
            "Record the catalyst and whether it turned out to be real. Over a year that log turns daily noise into a pattern you can use.",
            "Finally, watch related names. When a whole group moves together you are usually looking at a theme rather than a company.",
        ],
    },
    {
        "name": "Watchlists and routines",
        "focus": "build a watchlist, research routine, time management",
        "hooks": [
            "Most people do not have a watchlist. They have a graveyard of tickers they added at some ungodly hour and never looked at again.",
            "A watchlist only works if it has a job. Without one it becomes a source of notifications and regret.",
            "Research does not need to take an hour. It needs to happen consistently, which is a completely different problem.",
            "You do not need more information. You need a routine that fits inside a lunch break and survives a busy week.",
            "The most valuable investing habit costs about five minutes a day and almost nobody does it, because it is not exciting.",
            "A good research routine survives a bad week, a busy job and a boring market. If yours needs a quiet calendar to work, it is a hobby.",
            "You do not need to follow the whole market. You need to follow enough of it to know when something you own has actually changed.",
        ],
        "contexts": [
            "Here is the version that works. Split the list into three shelves. Core names you understand well enough to explain to a stranger. Themes worth learning about because they are moving the market. And a radar shelf for names that keep appearing in the news, which are not buys, just things worth understanding.",
            "Review the whole list once a week. Delete what you cannot explain. Add only what you actually researched. A short list you understand beats a long list you scroll, every single time.",
            "15 minutes, four steps. Scan what moved. Ask why. Read one thing that will still matter next month. Write two lines about what you learned and what you will watch tomorrow.",
            "Pick the same time every day and keep it short. The value is not in one session, it is in the record you build: what you expected, what happened, and what the gap taught you.",
        ],
        "insights": [
            "The order matters. Scan, then explain, then read something durable, then write. Skipping the last step is what turns research into entertainment, because nothing you learned gets stored.",
            "Pick a manageable number of names and go deep. Ten companies you understand beat 100 you recognize, and the depth is what stops you from panicking when one of them has a bad week.",
            "Reading with a question in hand beats reading from page one. What did revenue do compared to a year ago. Did margins expand or shrink. What did they say about next quarter. Three questions turn an unreadable document into a 15 minute task.",
            "Consistency beats intensity. Someone who spends five minutes a day reading will understand more after a year than someone who binges for a weekend and then ignores the market for a month.",
            "Reread your own notes from a month ago before you add anything new. Your past self asked more useful questions than most of what will appear in your feed today.",
        ],
        "extras": [
            "Keep the writing part small. Two lines is enough. The point is not documentation, it is that a written reason survives an emotional morning and an unwritten one does not.",
            "And put the list somewhere you cannot avoid it. Habits live in the places you already look, not in the places you mean to visit.",
            "Set a hard stop on scrolling too. When the routine is finished, close the app. Research that never ends becomes anxiety with extra steps.",
            "Keep the list short enough that you would notice a real change in any name on it. A list you cannot keep up with is decoration.",
            "Review the notes you wrote last month. Your own past questions are the best study guide you will ever get.",
            "Finally, batch the reading. One sitting at the same time each day beats checking in constantly and remembering nothing.",
        ],
    },
    {
        "name": "Risk and psychology",
        "focus": "risk management, trading psychology, discipline",
        "hooks": [
            "You can have a solid thesis, a clean entry and a good plan, and still lose because of what your brain does when the screen turns red.",
            "The market does not care how right you feel. It only cares how much you can lose when you are wrong.",
            "Risk management is the first skill and the last thing people learn, mostly because it is unglamorous and nobody makes videos about position sizing.",
            "Discipline is not a personality trait. It is a set of decisions made in advance so they are already decided when the market gets loud.",
            "Every investor has a strategy. Very few have a plan for the day the strategy feels awful.",
            "Fear and greed get the headlines. The two feelings that actually cost money are boredom and the need to be right.",
            "Losing money on a planned trade is a cost of doing business. Losing money on an unplanned one is a habit you can fix.",
        ],
        "contexts": [
            "Fear of missing out makes people buy strength. Loss aversion makes them hold losers and sell winners. Confirmation bias makes them read only the headlines that agree with them. None of that is a strategy problem. It is a wiring problem and it needs a process, not motivation.",
            "Three ideas carry most of the weight. Position size, because one position should never be able to damage the whole account. Scenario thinking, because a plan written in advance beats an improvisation made under stress. And diversification, because different risks keep three ideas from becoming one bet.",
            "A thesis without a falsification condition is a tattoo. Nothing in the market deserves that level of permanence, and the people who last treat their reasons as drafts.",
            "Notice what you do after a loss. If the next trade arrives faster, bigger and with less thought, you are not recovering, you are reacting. The gap between those two things is the discipline.",
        ],
        "insights": [
            "Write the plan before you need it. The reason, the risk, and the thing that would prove you wrong. Then score yourself afterwards on whether you followed the plan, not on whether it worked, because results are noisy and process is not.",
            "Cost basis is not physics. The market never asked what you paid, and the sooner that stops stinging the clearer every decision becomes.",
            "A loss you planned for is tuition. A loss you did not plan for is a leak. One makes you better and the other just makes you poorer.",
            "Volatility is not risk. Permanent loss is risk. That distinction sells a surprising number of products to people who never asked which one they were buying.",
            "Decide in advance how much you are willing to lose on an idea, and write it in the same place as the reason. A plan with no downside is a wish with a ticker.",
        ],
        "extras": [
            "And notice the incentive in the apps. Buying is one tap. Reviewing is buried. That asymmetry is designed, and knowing it exists is half the defence.",
            "One more: a green month tests discipline as much as a red one. Winning streaks are where bad habits get installed, because the feedback feels like validation.",
            "Decide the size before the reason. If a position is too large to think clearly about, no thesis will rescue the decision.",
            "Separate the outcome from the process. A good decision can lose money and a careless one can make it, which is why scoring yourself on process matters more.",
            "Know your own pattern. If you buy when you are bored or sell when you are tired, that is data about you rather than about the market.",
            "Finally, give decisions time. The market is open for hours and the urge to act usually passes faster than the news does.",
        ],
    },
    {
        "name": "Instruments",
        "focus": "ETFs, dividends, charts, analyst ratings, options basics",
        "hooks": [
            "Charts, dividends, ETFs, analyst notes. The tools of the market get taught as if everyone already knows what they are and why they exist.",
            "A chart is not a prediction. It is a record of what people paid, and a decent way to see how they felt about paying it.",
            "An analyst rating is an opinion with a number attached, and the number is only as good as the assumptions under it.",
            "A dividend looks like free money until you understand where it comes from, which is the company's own cash.",
            "Most investing terms are simple ideas wearing complicated uniforms. Learning to see through the uniform is the entire skill.",
            "Every instrument in the market is a compromise between something you want and something you give up. Learning the compromise is the education.",
            "Complex products are not more sophisticated. They are harder to describe, and sometimes that is the point.",
        ],
        "contexts": [
            "Take the two most common choices. A single stock is a bet on one company doing well, with concentrated upside and concentrated risk. An ETF is a basket, which gives up the moonshot in exchange for not being personally wiped out by one bad quarter.",
            "For a chart, three things matter. Price shows where the stock traded and where it repeatedly held. Volume shows how many people actually acted on the move. Trend shows direction, not destiny. Ranges matter more than any single candle.",
            "On ratings, notice three things. The direction of change matters more than the level, because it signals a shift. The house issuing the note may also do other work for the company. And targets published after a large move often ratify what already happened.",
            "Ask what problem the instrument solves before you ask how it performs. Income, growth, hedging and learning are different jobs, and the product that fits one can quietly damage another.",
        ],
        "insights": [
            "The useful question about any rating is never what the target is. It is what assumption would have to be true for that target to make sense, and whether you believe that assumption for reasons of your own.",
            "For dividends, check the durability before the yield. A payout is only as good as the cash flow behind it, and a very high yield attached to a shrinking business is a warning dressed as income.",
            "On charts, remember what they cannot tell you. No candle pattern contains the reason a stock gapped overnight. That answer lives in the news, the filing or the earnings report.",
            "With any instrument, ask what you are actually exposed to. If you cannot describe the risk in one sentence, you are not diversified, you are just uncertain in several directions at once.",
            "Read the cost line before the performance line on any fund. Fees are the one number that arrives regardless of what the market decides to do.",
        ],
        "extras": [
            "And write down what the instrument is for. Income, growth, hedging, learning. A tool used for the wrong job produces losses that look like bad luck.",
            "One more: paper trade anything new for a while before it touches real money. It is the cheapest tuition the market offers.",
            "Compare the costs as carefully as the story. Expense ratios, spreads and fees are the part of investing that is certain going in, so they deserve a look first.",
            "And know what the instrument cannot do. A dividend does not protect a falling price and a chart does not explain a business.",
            "Match the tool to the time horizon. Short horizons and long horizons need different instruments and very different expectations.",
            "Finally, if the terms are still fuzzy, write them down and find a plain explanation. Confusion gets expensive once contracts are involved.",
        ],
    },
    {
        "name": "Noise and understanding",
        "focus": "financial education, market noise, research habits",
        "hooks": [
            "There has never been more market information available, and there has never been less understanding of it. Those two facts are related.",
            "Every day you can read an enormous pile of headlines and still not know why a stock you own moved. Volume of words is not the same as clarity.",
            "Financial media optimizes for attention. Research should optimize for accuracy. Confusing the two is the most expensive habit in retail investing.",
            "Retail investors are not underinformed. They are overfed and unfiltered, which is a harder problem to solve than a lack of data.",
            "The market does not hide information anymore. It hides readability, and that is a much better disguise.",
            "An informed reader and a well fed reader look identical in a feed and behave nothing alike when the market turns.",
            "Attention is the scarcest input in investing, and the market has been engineered to spend yours.",
        ],
        "contexts": [
            "Narrow the funnel. Choose a small set of names you genuinely care about. Check them once a day instead of once an hour. Ask why something moved and accept the answer even when it is uninteresting. Write down what you learned, then close the app.",
            "That sounds too simple to matter, and it is the single biggest difference between people who learn the market and people who only react to it. Attention is the scarcest resource in investing and the market is built to spend it for you.",
            "Confidence without research is decoration. It looks like conviction from the outside and it behaves like a coin flip when the position goes against you.",
            "Most people do not choose their sources, they inherit them. A newsletter you joined years ago, an alert from an app, and a feed that rewards whatever is loudest today.",
        ],
        "insights": [
            "Fewer inputs, better questions, more understanding. That is the whole game, and it is available to anyone willing to be bored for 15 minutes a day.",
            "Understand the why before you react to the move. The reaction costs money, the understanding pays for itself, and they take roughly the same amount of time.",
            "Read one thing a day that will still be true next month. An earnings summary, a piece about how an industry works, a filing footnote. Daily noise expires. Structure does not.",
            "If a headline makes you feel like you must act immediately, treat that feeling as a warning sign rather than a signal. Urgency is manufactured far more often than it is real.",
            "Ask what a source is paid to do. Analysis pays for accuracy, media pays for attention and social platforms pay for reaction. Knowing the incentive explains most of what you read.",
        ],
        "extras": [
            "And keep the sources you trust short. Two or three places you actually read beat a feed you scroll past, because reading is a skill and scrolling is a habit.",
            "One more: log your own record, including the calls you got wrong. A private scorecard is the only performance review that does not flatter you.",
            "Notice how a headline makes you feel. Urgency, outrage and excitement usually mean the piece was written for engagement rather than understanding.",
            "Read the primary source at least once a week. A filing or a transcript read directly beats ten summaries written about it.",
            "Keep a list of what you were wrong about. That list teaches faster than any feed, because it is about your own reading rather than someone else's.",
            "Finally, decide what you will ignore. A short list of trusted sources is a filter, and a filter is what turns information into understanding.",
        ],
    },
]

# Batch 2 lines (ig_pools_2.py) extend every theme with extra contexts and
# insights. Kept in a separate file so new pool batches follow the same pattern
# as the draft batches (pools_11.py and friends).
import ig_pools_2 as _batch2  # noqa: E402

for _theme in THEMES:
    _extra = _batch2.EXTRA.get(_theme["name"])
    if not _extra:
        continue
    _theme["contexts"].extend(_extra["contexts"])
    _theme["insights"].extend(_extra["insights"])
