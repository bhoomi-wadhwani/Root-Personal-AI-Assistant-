import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from agents import orchestrator
from config import TELEGRAM_BOT_TOKEN
from memory import memory_store

_LOG_FILE = Path(__file__).parent / "logs" / "bot.log"
_LOG_FILE.parent.mkdir(exist_ok=True)

_fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
_file_handler = RotatingFileHandler(_LOG_FILE, maxBytes=2_000_000, backupCount=3, encoding="utf-8")
_file_handler.setFormatter(_fmt)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler(), _file_handler],
)
logger = logging.getLogger(__name__)

# Runtime cache — populated from disk on first message, saved after each turn
_sessions: dict[int, list[dict]] = {}

WELCOME = (
    "Hey! I'm your personal AI assistant — and I *remember* you.\n\n"
    "Here's what I can do:\n"
    "📧 *Gmail* — draft, send, or search your emails\n"
    "🔍 *Research* — search the web for anything\n"
    "🧠 *Memory* — I learn and remember things you tell me\n\n"
    "Just talk to me in plain English.\n\n"
    "Commands:\n"
    "/memory — see what I remember about you\n"
    "/forget — wipe all my memories about you\n"
    "/clear — reset just the chat history"
)


def _get_history(uid: int) -> list[dict]:
    if uid not in _sessions:
        _sessions[uid] = memory_store.get_history(uid)
    return _sessions[uid]


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id
    _sessions[uid] = []
    await update.message.reply_text(WELCOME, parse_mode="Markdown")


async def cmd_clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id
    _sessions[uid] = []
    memory_store.clear_history(uid)
    await update.message.reply_text(
        "Chat history cleared! I still remember who you are though. "
        "Use /forget if you want a total wipe."
    )


async def cmd_memory(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id
    facts = memory_store.get_facts(uid)
    if not facts:
        await update.message.reply_text(
            "I don't have any memories about you yet. Just chat with me and I'll start learning!"
        )
    else:
        lines = "\n".join(f"• {f}" for f in facts)
        await update.message.reply_text(f"Here's what I remember about you:\n\n{lines}")


async def cmd_forget(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id
    memory_store.clear_all(uid)
    _sessions[uid] = []
    await update.message.reply_text(
        "Done — I've wiped everything: memories and chat history. Completely fresh start!"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id
    text = update.message.text
    history = _get_history(uid)

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action="typing"
    )

    try:
        reply = orchestrator.run(text, history, uid)

        history.append({"role": "user", "content": text})
        history.append({"role": "assistant", "content": reply})
        _sessions[uid] = history[-30:]
        memory_store.update_history(uid, _sessions[uid])

        await update.message.reply_text(reply)
    except Exception as exc:
        logger.exception("Error handling message from %s", uid)
        await update.message.reply_text(
            f"Something went wrong: {exc}\n\nTry again or use /clear."
        )


def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN not set in .env")

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("clear", cmd_clear))
    app.add_handler(CommandHandler("memory", cmd_memory))
    app.add_handler(CommandHandler("forget", cmd_forget))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Assistant bot is running...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
