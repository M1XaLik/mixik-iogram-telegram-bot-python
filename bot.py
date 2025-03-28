import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from config import TOKEN  # Importing token from the configuration file

# Creating the bot object
bot = Bot(token=TOKEN)

# Creating the dispatcher
dp = Dispatcher()

# Handler for the /start command
@dp.message(Command("start"))
async def start_command_handler(message: types.Message):
    await message.reply("Hello! I'm an aiogram bot. How can I help you?")

# Main function to start the bot
async def main():
    print("Bot is running!")
    await dp.start_polling(bot)

# Entry point for the program
if __name__ == "__main__":
    asyncio.run(main())
