import logging

# Отримуємо кореневий логер
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG) # Встановлюємо загальний рівень для всіх логерів

# Створюємо обробник для консолі
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG) # Рівень для консолі

# Форматтер
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
console_handler.setFormatter(formatter)

# Додаємо обробник, тільки якщо його ще немає
if not root_logger.handlers: # Перевіряємо, чи немає обробників у кореневого логера
    root_logger.addHandler(console_handler)

logging.getLogger('apscheduler').setLevel(logging.DEBUG)  # рівень логування для APScheduler

# створюється об'єкт що має назву "telegram_bot"
logger = logging.getLogger("telegram_bot")
