import os
import asyncio
import random
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, BotCommand, ReactionTypeEmoji
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode
from aiogram.filters import Command

# ─── Load environment variables ───────────────────────────────────────────────
load_dotenv()
BOT_TOKENS = os.environ.get("BOT_TOKENS", "").split(",")
CHANNEL_URL = os.environ.get("CHANNEL_URL", "https://t.me/example")
GROUP_URL = os.environ.get("GROUP_URL", "https://t.me/example_group")

# ─── Emoji List ───────────────────────────────────────────────────────────────
EMOJIS = [
    "❤️", "👍", "🔥", "🥰", "👏", "😁", "🤔", "🤯", "😱", "🤬", "😢", "🎉",
    "🤩", "🤮", "💩", "🙏", "👌", "🕊️", "🤡", "🥱", "🥴", "😍", "🐳", "❤️‍🔥",
    "🌚", "🌭", "💯", "🤣", "⚡", "🍌", "🏆", "💔", "🤨", "😐", "🍓", "🍾",
    "💋", "🖕", "😈", "😴", "😭", "🤓", "👻", "👨‍💻", "👀", "🎃", "🙈", "😇",
    "😨", "🤝", "✍️", "🤗", "🫡", "🎅", "🎄", "☃️", "💅", "🤪", "🗿", "🆒",
    "💘", "🙉", "🦄", "😘", "💊", "🙊", "😎", "👾", "🤷‍♂️", "🤷", "🤷‍♀️", "😡"
]

# ─── Dummy HTTP server for health check ───────────────────────────────────────
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def start_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), DummyHandler)
    print(f"🌐 Dummy server listening on port {port}")
    server.serve_forever()

# ─── Setup Dispatcher for a given token ───────────────────────────────────────
def setup_dispatcher(token: str):
    bot = Bot(token=token, parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    # ─── /start command handler ───────────────────────────────────────────────
    @dp.message(Command("start"))
    async def start_cmd(message: Message):
        kb = InlineKeyboardBuilder()
        kb.button(text="Updates", url=CHANNEL_URL)
        kb.button(text="Support", url=GROUP_URL)
        kb.button(text="➕ Add Me To Group", url=f"https://t.me/{(await bot.get_me()).username}?startgroup=true")
        kb.adjust(2, 1)

        await message.answer(
            "👋 Hey there! I'm <b>ReactionBot</b>.\n\n"
            "I automatically react to messages in your group with fun emojis like ❤️🔥🎉👌.\n\n"
            "Just add me to your group and enjoy the reactions!\n\n"
            "P.S. I work best when you give me admin powers 😉",
            reply_markup=kb.as_markup()
        )

    # ─── React to any normal text message ─────────────────────────────────────
    @dp.message(F.text & ~F.text.startswith("/"))
    async def react_to_message(message: Message):
        emoji = random.choice(EMOJIS)
        try:
            await bot.set_message_reaction(
                chat_id=message.chat.id,
                message_id=message.message_id,
                reaction=[ReactionTypeEmoji(emoji=emoji)]
            )
            print(f"✨ Reacted to msg {message.message_id} in chat {message.chat.id} with {emoji}")
        except Exception as e:
            print(f"❌ Error reacting to msg {message.message_id}: {e}")

    return bot, dp

# ─── Main Async Entry ─────────────────────────────────────────────────────────
async def main():
    tasks = []

    for token in BOT_TOKENS:
        token = token.strip()
        if not token:
            continue
        try:
            bot, dp = setup_dispatcher(token)
            await bot.set_my_commands([BotCommand(command="start", description="Start the bot")])
            username = (await bot.get_me()).username
            print(f"✅ @{username} is ready.")
            tasks.append(dp.start_polling(bot, allowed_updates=["message"]))
        except Exception as e:
            print(f"❌ Failed to start bot with token {token[:10]}: {e}")

    print(f"🚦 Starting {len(tasks)} bot(s)…")
    await asyncio.gather(*tasks)

# ─── Program Entry Point ──────────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        print("🔁 Launching Reaction Bot system...")
        threading.Thread(target=start_dummy_server, daemon=True).start()
        asyncio.run(main())
    except Exception as e:
        print(f"🔥 Fatal error in main(): {e}")