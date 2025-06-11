import os
import asyncio
import random
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from aiogram import Bot, Dispatcher, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command
from aiogram.types import DefaultBotProperties, ReactionTypeEmoji
from dotenv import load_dotenv

# ─── Load .env ────────────────────────────────────────────────────────────────
load_dotenv()

BOT_TOKENS  = os.environ.get("BOT_TOKENS", "").split(",")
CHANNEL_URL = os.environ.get("CHANNEL_URL", "https://t.me/example")
GROUP_URL   = os.environ.get("GROUP_URL",   "https://t.me/example_group")

EMOJIS = [
    "❤️", "👍", "🔥", "🥰", "👏", "😁", "🤔", "🤯", "😱", "🤬", "😢", "🎉",
    "🤩", "🤮", "💩", "🙏", "👌", "🕊️", "🤡", "🥱", "🥴", "😍", "🐳", "❤️‍🔥",
    "🌚", "🌭", "💯", "🤣", "⚡", "🍌", "🏆", "💔", "🤨", "😐", "🍓", "🍾",
    "💋", "🖕", "😈", "😴", "😭", "🤓", "👻", "👨‍💻", "👀", "🎃", "🙈", "😇",
    "😨", "🤝", "✍️", "🤗", "🫡", "🎅", "🎄", "☃️", "💅", "🤪", "🗿", "🆒",
    "💘", "🙉", "🦄", "😘", "💊", "🙊", "😎", "👾", "🤷‍♂️", "🤷", "🤷‍♀️", "😡"
]

# ─── Dispatcher Factory ───────────────────────────────────────────────────────
def setup_dispatcher(token: str):
    # ✅ Use DefaultBotProperties to silence parse_mode deprecation warning
    bot = Bot(token=token, default=DefaultBotProperties(parse_mode="HTML"))
    dp  = Dispatcher()

    # ── Startup Handler ────────────────────────────────────────────────────
    async def on_startup(bot: Bot):
        try:
            print(f"⚙️ Bot @{(await bot.get_me()).username} starting up…")
            await bot.set_my_commands([
                types.BotCommand(command="start", description="Show welcome message and commands")
            ])
            print(f"✅ Commands set for @{(await bot.get_me()).username}")
        except Exception as e:
            print(f"❌ Startup error for bot {token[:10]}: {e}")

    dp.startup.register(on_startup)

    # ── /start Command ─────────────────────────────────────────────────────
    @dp.message(Command(commands=["start"]))
    async def cmd_start(message: types.Message):
        try:
            print(f"🚀 /start received in chat {message.chat.id}")
            kb = InlineKeyboardBuilder()
            kb.button(text="Updates", url=CHANNEL_URL)
            kb.button(text="Support", url=GROUP_URL)
            kb.button(
                text="Add Me To Your Group",
                url=f"https://t.me/{(await message.bot.get_me()).username}?startgroup=true"
            )
            kb.adjust(2, 1)

            await message.answer(
                "👋 Hey there! I'm <b>ReactionBot</b>.\n\n"
                "I automatically react to messages in your group with fun and random emojis like ❤️🔥🎉👌.\n\n"
                "Just add me to your group and enjoy the reactions!\n\n"
                "P.S. I work best when I have a little admin magic 😉",
                reply_markup=kb.as_markup()
            )
            print(f"✅ Welcome message sent to chat {message.chat.id}")
        except Exception as e:
            print(f"❌ /start handler error in chat {message.chat.id}: {e}")

    # ── Auto Reaction Handler ──────────────────────────────────────────────
    @dp.message()
    async def react(message: types.Message):
        try:
            if message.text and not message.text.startswith("/"):
                emoji = random.choice(EMOJIS)
                print(f"🎯 Reacting to msg {message.message_id} in chat {message.chat.id} with {emoji}")

                await message.bot.set_message_reaction(
                    chat_id=message.chat.id,
                    message_id=message.message_id,
                    reaction=[ReactionTypeEmoji(emoji=emoji)]
                )

                print(f"✨ Reaction sent to msg {message.message_id} in chat {message.chat.id}")
        except Exception as e:
            print(f"❌ Reaction error in chat {message.chat.id}: {e}")

    return bot, dp

# ─── Run All Bots ─────────────────────────────────────────────────────────────
async def main():
    runners = []

    for token in BOT_TOKENS:
        token = token.strip()
        if not token:
            continue

        try:
            bot, dp = setup_dispatcher(token)
            username = (await bot.get_me()).username
            print(f"🧵 Initialized bot @{username} with token {token[:10]}…")
            runners.append(dp.start_polling(bot, timeout=20, allowed_updates=["message"]))
        except Exception as e:
            print(f"❌ Failed to init/start bot {token[:10]}: {e}")

    print(f"🚦 Starting polling for {len(runners)} bots…")
    await asyncio.gather(*runners)

# ─── Dummy HTTP Server (for Render health check) ──────────────────────────────
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"AFK bot is alive!")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def start_dummy_server():
    port = int(os.environ.get("PORT", 10000))  # Render injects this
    server = HTTPServer(("0.0.0.0", port), DummyHandler)
    print(f"🌐 Dummy server listening on port {port}")
    server.serve_forever()

# ─── Main Entry Point ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        print("🔁 Launching bot system…")

        # Start dummy HTTP server in a background thread
        threading.Thread(target=start_dummy_server, daemon=True).start()

        # Start asyncio event loop for all bots
        asyncio.run(main())

    except Exception as e:
        print(f"🔥 Fatal error in main(): {e}")