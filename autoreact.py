import os
import asyncio
import random
from aiogram import Bot, Dispatcher, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command
from dotenv import load_dotenv

# ─── Imports for Dummy HTTP Server ──────────────────────────────────────────
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

load_dotenv()

BOT_TOKENS = os.environ.get("BOT_TOKENS", "").split(",")
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

# Store dispatcher instances
dispatchers = []

@dispatchers.append
def setup_dispatcher(token: str):
    bot = Bot(token=token, parse_mode="HTML")
    dp  = Dispatcher()

    # ─── Bot Startup ──────────────────────────────────────────────────────
    async def on_startup(bot: Bot):
        try:
            print(f"⚙️ Bot @{(await bot.get_me()).username} is starting up...")
            await bot.set_my_commands([
                types.BotCommand(command="start", description="Show welcome message and commands")
            ])
            print(f"✅ Commands set for @{(await bot.get_me()).username}")
        except Exception as e:
            print(f"❌ Error during startup of bot {token[:10]}: {e}")

    dp.startup.register(on_startup)

    # ─── /start Command ───────────────────────────────────────────────────
    @dp.message(Command(commands=["start"]))
    async def cmd_start(message: types.Message):
        try:
            print(f"🚀 /start received in chat {message.chat.id}")
            kb = InlineKeyboardBuilder()
            kb.button(text="Updates", url=CHANNEL_URL)
            kb.button(text="Support", url=GROUP_URL)
            kb.button(text="Add Me To Your Group", url=f"https://t.me/{(await message.bot.get_me()).username}?startgroup=true")
            kb.adjust(2, 1)

            await message.answer(
                "👋 Hey there! I'm <b>ReactionBot</b>.\n\n"
                "I automatically react to messages in your group with fun and random emojis like ❤️🔥🎉👌.\n"
                "Just add me to your group and enjoy the reactions!\n"
                "P.S. I work best when I have a little admin magic 😉",
                reply_markup=kb.as_markup()
            )
            print(f"✅ Welcome message sent to chat {message.chat.id}")
        except Exception as e:
            print(f"❌ Error in /start handler for chat {message.chat.id}: {e}")

    # ─── Regular Message Reaction ─────────────────────────────────────────
    @dp.message()
    async def react(message: types.Message):
        try:
            if message.text and not message.text.startswith("/"):
                emoji = random.choice(EMOJIS)
                print(f"🎯 Reacting to message {message.message_id} in chat {message.chat.id} with emoji {emoji}")
                await message.bot.send_message_reaction(
                    chat_id=message.chat.id,
                    message_id=message.message_id,
                    emoji=emoji
                )
                print(f"✨ Reaction sent to message {message.message_id} in chat {message.chat.id}")
        except Exception as e:
            print(f"❌ Reaction error in chat {message.chat.id}: {e}")

    return bot, dp

# ─── Run All Bots ────────────────────────────────────────────────────────
async def main():
    runners = []
    for token in BOT_TOKENS:
        try:
            bot, dp = setup_dispatcher(token.strip())
            username = (await bot.get_me()).username
            print(f"🧵 Initialized bot @{username} with token {token[:10]}...")
            runners.append(dp.start_polling(bot, timeout=20, allowed_updates=["message"]))
        except Exception as e:
            print(f"❌ Failed to init/start bot {token[:10]}: {e}")

    print(f"🚦 Starting polling for {len(runners)} bots...")
    await asyncio.gather(*runners)
    
# ─── Dummy HTTP Server to Keep Render Happy ─────────────────────────────────
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
    print(f"Dummy server listening on port {port}")
    server.serve_forever()

# ─── Main Entry Point ────────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        print("🔁 Launching bot system...")
        
    # Start dummy HTTP server (needed for Render health check)
    threading.Thread(target=start_dummy_server, daemon=True).start()
        asyncio.run(main())
    except Exception as e:
        print(f"🔥 Fatal error in main(): {e}")
