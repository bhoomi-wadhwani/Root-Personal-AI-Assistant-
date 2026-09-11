# Personal AI Assistant — Telegram Bot

A fully working multi-agent AI assistant that lives in Telegram. Talk to it in plain English — it figures out what you need, routes the task to the right specialist agent, and gets it done.

**Live features:** Send emails via Gmail · Search the web · Remember you across conversations · LinkedIn automation

---

## Architecture

```
User (Telegram)
      │
      ▼
 Orchestrator Agent          ← routes based on intent
  ├── Gmail Agent            ← draft / send / search emails via Gmail API
  ├── Research Agent         ← web search via DuckDuckGo
  └── LinkedIn Agent         ← search people, connect, message
      
 Memory Store                ← persists facts + chat history per user
```

The orchestrator uses LLM-native tool calling (not hardcoded if/else) to route tasks. It reads the user's message and conversation history, decides which specialist to call, passes a task description, and synthesizes the result back into a natural response.

---

## What it can do

| Say this... | What happens |
|---|---|
| "Draft an email to my professor about missing class" | Research agent gathers context → Gmail agent drafts and sends |
| "Who is the CTO of Zepto?" | Research agent searches the web and summarizes |
| "Remember that I prefer formal email tone" | Fact saved to persistent memory, applied to all future emails |
| "Find Priya Sharma on LinkedIn and send her a connection request" | LinkedIn agent searches, finds profile, sends request |

---

## Tech stack

- **Python 3.11** — async throughout (python-telegram-bot v20)
- **Groq API** — LLM inference (fast, free tier available)
- **Gmail API** — OAuth 2.0, real email send/receive
- **DuckDuckGo** — free web search, no API key needed
- **Telegram Bot API** — polling-based bot
- **Rotating file logs** — production-style logging

---

## Setup

```bash
git clone https://github.com/YOUR_USERNAME/telegram-assistant
cd telegram-assistant
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in:

```
TELEGRAM_BOT_TOKEN=your_token        # from @BotFather
GROQ_API_KEY=your_key                # from console.groq.com (free)
```

For Gmail: follow the [Gmail API quickstart](https://developers.google.com/gmail/api/quickstart/python) to get `gmail_credentials.json`, then run once to authorize.

```bash
python main.py
```

---

## Project structure

```
telegram-assistant/
├── main.py                  # Telegram bot entry point
├── config.py                # Env config
├── agents/
│   ├── orchestrator.py      # LLM router with tool calling
│   ├── gmail_agent.py       # Gmail specialist
│   ├── research_agent.py    # Web search specialist
│   └── linkedin_agent.py    # LinkedIn specialist
├── tools/
│   ├── gmail_tools.py       # Gmail API wrapper
│   ├── search_tools.py      # DuckDuckGo wrapper
│   └── linkedin_tools.py    # LinkedIn automation
├── memory/                  # Per-user persistent memory
└── requirements.txt
```

---

## Why I built this

Most AI assistants are demos — they don't actually do anything. This one is live, connected to real services, and handles real workflows end to end. The goal was to build something that proves multi-agent systems work beyond toy examples.
