# Root — Personal AI Assistant

> A fully working multi-agent AI assistant that lives in your Telegram. Talk to it in plain English — it figures out what you need, routes the task to the right specialist agent, and gets it done.

**Live capabilities:** Send & search Gmail · Web research · Persistent memory · LinkedIn automation

---

## How it works

```
You (Telegram)
      │
      ▼
 Orchestrator Agent          ← reads your message, decides who handles it
  ├── Gmail Agent            ← draft / send / search real emails via Gmail API
  ├── Research Agent         ← live web search via DuckDuckGo
  └── LinkedIn Agent         ← search profiles, send connection requests, message
      
 Memory Store                ← remembers facts + full chat history per user (persisted to disk)
```

The orchestrator uses LLM-native tool calling — no hardcoded if/else routing. It reads your message and conversation history, picks the right specialist, and synthesizes a natural reply from the result.

---

## What you can say

| Message | What happens |
|---|---|
| "Draft an email to my professor about missing tomorrow's class" | Gmail agent drafts it and sends |
| "Who is the CTO of Zepto?" | Research agent searches the web and summarizes |
| "Remember I prefer formal tone in emails" | Fact saved to memory, applied to all future emails automatically |
| "Find Priya Sharma on LinkedIn and send a connection request" | LinkedIn agent searches, finds the profile, sends the request |
| `/memory` | Shows everything the bot has learned about you |
| `/forget` | Wipes all memory and history — clean slate |

---

## Tech stack

| Layer | Tech |
|---|---|
| Bot framework | python-telegram-bot v20 (async) |
| LLM inference | Groq API (llama3-70b — fast, free tier) |
| Email | Gmail API with OAuth 2.0 |
| Web search | DuckDuckGo (no API key needed) |
| LinkedIn | Selenium-based automation |
| Memory | JSON files per user, loaded on demand |
| Logs | Rotating file handler (production-style) |

---

## Setup

```bash
git clone https://github.com/bhoomi-wadhwani/Root-Personal-AI-Assistant-
cd Root-Personal-AI-Assistant-
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your credentials:

```env
TELEGRAM_BOT_TOKEN=your_token        # from @BotFather on Telegram
GROQ_API_KEY=your_key                # from console.groq.com — free tier works
```

**Gmail setup (one-time):**
1. Follow the [Gmail API quickstart](https://developers.google.com/gmail/api/quickstart/python) to create a project and download `gmail_credentials.json`
2. Place it in the project root
3. Run `python main.py` once — a browser window will open to authorize your Gmail account
4. A `gmail_token.json` is saved locally; you won't need to re-authorize

```bash
python main.py
```

---

## Project structure

```
Root-Personal-AI-Assistant/
├── main.py                  # Bot entry point — handlers, session management
├── config.py                # Loads env vars
├── requirements.txt
├── .env.example             # Template — copy to .env and fill in
├── agents/
│   ├── orchestrator.py      # LLM router with tool calling
│   ├── gmail_agent.py       # Gmail specialist
│   ├── research_agent.py    # Web search specialist
│   └── linkedin_agent.py    # LinkedIn specialist
├── tools/
│   ├── gmail_tools.py       # Gmail API wrapper
│   ├── search_tools.py      # DuckDuckGo wrapper
│   └── linkedin_tools.py    # LinkedIn automation
└── memory/
    └── memory_store.py      # Per-user fact + history persistence
```

---

## Why I built this

Most AI assistants are demos — they don't actually do anything. This one is live, connected to real services, and handles real workflows end to end. The goal was to prove that multi-agent systems work beyond toy examples and that a Telegram bot can be a genuinely useful daily driver.
