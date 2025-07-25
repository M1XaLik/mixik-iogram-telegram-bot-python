import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import config
import handlers # import commands realisation
import database_manager
import scheduler # планувальник (import scheduler)

from logger import logger  # import logger

# Створення об'єкта бота
bot = Bot(token=config.BOT_TOKEN)

# Створення диспетчера з зберіганням станів
dp = Dispatcher(storage=MemoryStorage())


# Головна функція для запуску бота
async def main():
    # 1 Ініціалізація бази даних
    # Database init
    logger.info("Starting database initialization...")
    try:
        database_manager.init_database()
        logger.info("Database successfully initialized.")
    except Exception as e:
        logger.critical(f"Critical error during database initialization: {e}", exc_info=True)
        return

    # 2. Реєстрація обробників
    logger.info("Registering handlers...")
    try:
        handlers.register_handlers(dp)
        logger.info("Handlers successfully registered.")
    except Exception as e:
        logger.critical(f"Critical error during handlers registration: {e}", exc_info=True)
        return

    # 3. Реєстрація планувальника
    logger.info("Starting scheduler...")
    try:
        scheduler.setup_bot_scheduler(bot)
    except Exception as e:
        logger.critical(f"Critical error during scheduler startup: {e}", exc_info=True)
        # Якщо планувальник не запустився, бот продовжить працювати, але без автоматичних нагадувань.

    # 4. Запуск бота
    logger.info("Bot is running!")
    await bot.delete_webhook(drop_pending_updates=True) # щоб видалити всі вебхуки (оновлення), які накопичились в телеграмі за цей час
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.critical(f"Unexpected error during bot startup: {e}", exc_info=True) # exc_info=True додасть до логу повне трасування стека
