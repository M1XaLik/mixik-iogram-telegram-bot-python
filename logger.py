import logging

logging.basicConfig(
    level=logging.DEBUG,  # Змініть на logging.DEBUG для детальнішого логування
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)

logger = logging.getLogger("telegram_bot")
