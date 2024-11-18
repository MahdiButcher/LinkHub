from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import logging
import asyncio
import sqlite3
from magic_filter import F

from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types.web_app_info import WebAppInfo

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize Dispatcher
dp = Dispatcher()

# Initialize SQLite connection
conn = sqlite3.connect("web_panels.db")
cursor = conn.cursor()

# Create table if it does not exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS web_panels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    url TEXT
)
""")
conn.commit()

# Function to add a new web panel URL to the database
def add_web_panel(user_id: int, url: str):
    cursor.execute("INSERT INTO web_panels (user_id, url) VALUES (?, ?)", (user_id, url))
    conn.commit()

# Function to get all web panel URLs
def get_web_panels():
    cursor.execute("SELECT url FROM web_panels")
    return cursor.fetchall()

# Handler for the /start command
@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    # Fetch all stored web panel URLs
    web_panels = get_web_panels()
    buttons = []

    # Create InlineKeyboardButtons for each stored web panel
    for panel in web_panels:
        url = panel[0]
        buttons.append([InlineKeyboardButton(text=url, web_app=WebAppInfo(url=url))])

    # Add an option for users to submit their own URL
    buttons.append([InlineKeyboardButton(text="Submit Your Web Panel URL", callback_data="submit_url")])

    # Display buttons to the user
    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await message.answer(
        "Welcome! Click a button below to access a web panel or submit your own:",
        reply_markup=inline_keyboard
    )

# Handler for user URL submission using Magic Filter
@dp.callback_query(F.data == "submit_url")
async def handle_submit_url(callback_query: types.CallbackQuery):
    await callback_query.message.answer("Please send me your web panel URL (e.g., https://yourwebpanel.com).")

# Handler to capture the URL sent by the user using Magic Filter
@dp.message(F.text.startswith("http") & (F.text.contains("://")))
async def save_user_url(message: types.Message):
    user_id = message.from_user.id
    url = message.text.strip()

    # Save the user's URL in the database
    add_web_panel(user_id, url)
    
    await message.answer("Your web panel URL has been added! Use /start to see it listed.")

async def main() -> None:
    # Initialize Bot instance with default bot properties
    bot = Bot(
        token="token"
    )

    # Start polling
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
