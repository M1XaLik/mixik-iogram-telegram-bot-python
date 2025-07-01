import logging
from aiogram import Bot
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import random

import config # Імпортуємо конфігурацію для медіа та налаштувань планувальника
import database_manager # Імпортуємо менеджер БД для отримання іменинників

from logger import logger  # import logger


async def send_daily_birthday_reminders_task(bot_instance: Bot):
    """
    Scheduled task to check for today's birthdays and send reminders to the specified chats.
    This function runs periodically via APScheduler.

    Отримуємо сьогоднішні нагадування про дні народження з бази даних
    Функція get_birthday_reminders_for_today повертає:
    (id, creator_telegram_user_id, birthday_person_identifier, birthdate, chat_id_to_notify, telegram_chat_name, telegram_chat_type)
    """
    logger.info("Executing daily birthday reminder job. Checking for today's birthdays...")
    
    try:
        today_birthdays = database_manager.get_birthday_reminders_for_today()

        logger.debug(f"Found {len(today_birthdays)} birthday reminders for today.")

        if not today_birthdays:
            logger.info("No birthdays found for today.")
            return

        for reminder in today_birthdays:
            try:
                # Розпаковуємо дані з кортежу
                # Tuple unpacking
                # Назви змінних збігаються з назвами колонок у БД
                (
                    reminder_id,
                    creator_telegram_user_id, 
                    birthday_person_identifier, 
                    birthdate, 
                    chat_id_to_notify, 
                    telegram_chat_name,
                    telegram_chat_type
                ) = reminder

                logger.debug(f"Preparing to send birthday reminder for '{birthday_person_identifier}' (Born: {birthdate}) to chat ID {chat_id_to_notify} ({telegram_chat_name}, type: {telegram_chat_type}).")

                # Формуємо повідомлення
                # Використовуємо birthday_person_identifier, яке може бути як ім'ям, так і @username
                # Також можна додати рік, якщо він є у birthdate
                display_date = birthdate
                if len(birthdate) == 10: # Якщо формат YYYY-MM-DD
                    year = birthdate.split('-')[0]
                    display_date = f"{birthdate[5:]}.{year}" # Наприклад, 05-15.1990 TODO: розібратися із записом
                
                message_text = (
                    f"🎉 **Сьогодні День народження у {birthday_person_identifier}!**\n"
                    f"🎂 Дата народження: {display_date}" # Використовуємо display_date
                )
                
                # Надсилаємо повідомлення у вказаний чат
                await bot_instance.send_message(
                    chat_id=chat_id_to_notify, 
                    text=message_text,
                    parse_mode="Markdown" # Використовуємо Markdown для жирного тексту
                )
                # GIF
                if config.BIRTHDAY_GIFS:
                    await bot_instance.send_animation(
                        chat_id=chat_id_to_notify,
                        animation=random.choice(config.BIRTHDAY_GIFS)
                    )
                # тексти привітань
                if config.BIRTHDAY_TEXTS:
                    await bot_instance.send_message(
                        chat_id=chat_id_to_notify,
                        text=random.choice(config.BIRTHDAY_TEXTS)
                    )

                logger.info(f"Successfully sent birthday reminder for '{birthday_person_identifier}' to chat ID {chat_id_to_notify}.")

            except Exception as e:
                # Логуємо помилку для конкретного нагадування, не зупиняючи обробку інших
                logger.error(f"Failed to send birthday reminder for '{reminder[2]}' (ID: {reminder[0]}) to chat ID {reminder[4]}: {e}", exc_info=True)

    except Exception as e:
        logger.critical(f"Critical error in send_daily_birthday_reminders: {e}", exc_info=True)


def setup_bot_scheduler(bot: Bot) -> AsyncIOScheduler:
    """
    Initializes and configures APScheduler for the bot.
    All scheduled jobs should be added here.

    Args:
        bot (Bot): The Bot instance to pass to scheduled jobs.
    
    Returns:
        AsyncIOScheduler: Configured scheduler instance.
    """
    
    try:

        scheduler = AsyncIOScheduler(timezone=config.SCHEDULER_TIMEZONE)

        # Add the daily birthday reminder job
        scheduler.add_job(
            send_daily_birthday_reminders_task,
            CronTrigger(
                hour=config.BIRTHDAY_REMINDER_HOUR,
                minute=config.BIRTHDAY_REMINDER_MINUTE,
                second=0,  # Запускаємо на початку хвилини
                timezone=config.SCHEDULER_TIMEZONE
            ),
            args=(bot,), # Pass the bot object as an argument to the task function || передаємо об'єкт бота як аргумент до функції завдання
            id='daily_birthday_check', # Unique ID for the job
            name='Daily Birthday Check Task',
            replace_existing=True,
            misfire_grace_time=config.SCHEDULER_MISFIRE_GRACE_TIME
        )
        logger.info("Daily birthday reminder job added to scheduler.")


        # FUTURE:
        # Add other scheduled tasks here as needed:
        # Example: scheduler.add_job(your_other_async_function, 'interval', minutes=30, args=(bot,))


        try:
            scheduler.start()  # Start the scheduler
            logger.info("Scheduler successfully started.")
        except Exception as e:
            logger.critical(f"Failed to start the scheduler: {e}", exc_info=True)
        
        # при успіху
        return scheduler
    except Exception as e:
        logger.critical(f"Failed to start the scheduler: {e}", exc_info=True)