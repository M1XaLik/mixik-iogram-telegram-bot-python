import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import config  # Import configurations
import handlers  # Import handlers

# Creating the bot object
bot = Bot(token=config.BOT_TOKEN)

# Creating the dispatcher with state storage
dp = Dispatcher(storage=MemoryStorage())

# Register handlers (imported from handlers.py)
handlers.register_handlers(dp)

# Main function to start the bot
async def main():
    print("Bot is running!")
    await dp.start_polling(bot)

# Entry point for the program
if __name__ == "__main__":
    asyncio.run(main())
