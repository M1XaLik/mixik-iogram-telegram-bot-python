import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import config
import handlers # import commands realisation
from logger import logger  # import logger

# Створення об'єкта бота
bot = Bot(token=config.BOT_TOKEN)

# Створення диспетчера з зберіганням станів
dp = Dispatcher(storage=MemoryStorage())

# Реєстрація обробників
handlers.register_handlers(dp)
logger.info("Handlers registered and bot is initialized.")

# Головна функція для запуску бота
async def main():
    logger.info("Bot is running!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
