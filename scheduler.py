import logging
from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import random

import config # Імпортуємо конфігурацію для медіа та налаштувань планувальника
import database_manager # Імпортуємо менеджер БД для отримання іменинників

from logger import logger  # import logger


async def send_birthday_reminders_task(bot: Bot):
    """
    Scheduled task to check for today's birthdays and send reminders.
    This function runs periodically via APScheduler.
    """

    logger.info("Checking for today's birthdays to send reminders...")
    
    try:
        # Get today's birthdays from the database
        today_birthdays = database_manager.get_today_birthdays()

        if not today_birthdays:
            logger.info("No birthdays found for today.")
            return

        for user_id, name in today_birthdays:
            logger.debug(f"Preparing to send birthday reminder for {name} to user {user_id}")
            try:
                # Send the birthday messages
                await bot.send_message(
                    chat_id=user_id, 
                    text=f"Сьогодні День народження в 👉🏿 {name}!" # Reminder message
                )
                # await bot.send_animation(
                #     chat_id=user_id, 
                #     animation=random.choice(config.BIRTHDAY_GIFS) # Random GIF from config
                # )
                # await bot.send_message(
                #     chat_id=user_id, 
                #     text=random.choice(config.BIRTHDAY_TEXTS) # Random text from config
                # )
                logger.info(f"Successfully sent birthday reminders for {name} to user {user_id}.")
            except Exception as user_e:
                logger.error(f"Failed to send birthday reminder to user {user_id} ({name}): {user_e}", exc_info=True)
                # This could be due to user blocking the bot, invalid user_id, etc.

    except Exception as e:
        logger.critical(f"Critical error in send_birthday_reminders_task: {e}", exc_info=True)


def setup_bot_scheduler(bot: Bot) -> AsyncIOScheduler:
    """
    Initializes and configures APScheduler for the bot.
    All scheduled jobs should be added here.

    Args:
        bot (Bot): The Bot instance to pass to scheduled jobs.
    
    Returns:
        AsyncIOScheduler: Configured scheduler instance.
    """
    scheduler = AsyncIOScheduler(timezone=config.SCHEDULER_TIMEZONE)

    # Add the daily birthday reminder job
    scheduler.add_job(
        send_birthday_reminders_task,
        'cron',
        hour=config.BIRTHDAY_REMINDER_HOUR,
        minute=config.BIRTHDAY_REMINDER_MINUTE,
        args=(bot,), # Pass the bot object as an argument to the task function
        id='daily_birthday_check', # Unique ID for the job
        name='Daily Birthday Check Task',
        misfire_grace_time=config.SCHEDULER_MISFIRE_GRACE_TIME
    )
    logger.info("Daily birthday reminder job added to scheduler.")

    # FUTURE:
    # Add other scheduled tasks here as needed:
    # Example: scheduler.add_job(your_other_async_function, 'interval', minutes=30, args=(bot,))

    return scheduler