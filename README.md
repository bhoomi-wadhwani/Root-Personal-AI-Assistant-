# Root — Personal AI Assistant

A multi-agent AI assistant that lives in Telegram. Send it a message in plain English and it figures out what you need, routes it to the right specialist agent, and gets it done — send emails, search the web, automate LinkedIn, remember things across conversations.

## What it does

The orchestrator reads your message and conversation history, decides which agent handles it, and synthesises a natural reply. No hardcoded if/else routing — it uses LLM tool calling to make that decision.

Gmail agent drafts and sends real emails via the Gmail API. Research agent does live web searches. LinkedIn agent can find profiles and send connection requests. Memory store saves facts you tell it and applies them automatically to future tasks.

## Stack

Groq API - the LLM powering all three agents. Groq runs Llama models with very low latency which matters for a conversational assistant where response time is noticeable.

python-telegram-bot - the Telegram bot framework. Handles incoming messages, commands like /memory and /forget, and sending replies back.

Gmail API (google-auth, google-api-python-client) - lets the Gmail agent read, draft and send real emails from your Gmail account. Uses OAuth2 so credentials are stored locally after a one-time browser authorisation.

DuckDuckGo Search - the research agent uses this for live web searches. No API key needed.

Selenium - used by the LinkedIn agent to automate browser actions like searching profiles and sending connection requests. LinkedIn has no official API for this so browser automation is the only option.

Memory store (JSON files) - each user gets their own JSON file storing facts they have shared and their conversation history. Loaded on demand so the assistant remembers context across sessions.

Python logging with RotatingFileHandler - all agent activity is logged to a rotating file so you can trace what each agent did without the logs growing unboundedly.