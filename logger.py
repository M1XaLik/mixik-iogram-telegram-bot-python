import logging

logging.basicConfig(
    level=logging.DEBUG,  # рівень логування
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)

# створюється об'єкт що має назву "telegram_bot"
logger = logging.getLogger("telegram_bot")
