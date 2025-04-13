import re
from aiogram import F, Dispatcher, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

import config  # Import configuration
from logger import logger  # import logger

# Define states for user input
class UserBirthday(StatesGroup):
    name = State()
    birthdate = State()

# Handler for the /start command
async def start_command_handler(message: types.Message):
    logger.info(f"Received /start from user {message.from_user.id}")
    await message.reply(config.startMessage, parse_mode="HTML")

# Handler for the /help command
async def help_command_handler(message: types.Message):
    logger.info(f"Received /help from user {message.from_user.id}")
    await message.reply(config.commandsList, parse_mode="HTML")

# Допоміжна функція для перевірки, чи повідомлення надсилає користувач,
# який ініціював ланцюг введення даних
async def check_authorization(message: types.Message, state: FSMContext) -> bool:
    data = await state.get_data()
    author_id = data.get("author_id")
    if author_id is None:
        logger.debug("No author_id found in state. Allowing operation.")
        return True
    if message.from_user.id != author_id:
        logger.warning(f"Unauthorized access attempt by user {message.from_user.id}. Expected {author_id}.")
        await message.reply("❌ You are not allowed to continue this operation.")
        return False
    logger.debug("User authorization passed.")
    return True

# 1
# /new – start commands chain
async def new_birthday_handler(message: types.Message, state: FSMContext):
    logger.info(f"Initiating new birthday chain for user {message.from_user.id}")
    # Зберігаємо id користувача, який ініціював ланцюг
    await state.update_data(author_id=message.from_user.id)

    # Створюємо inline-кнопку для скасування операції
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("❌ Cancel", callback_data="cancel"))

    await message.reply(
        "<b>Enter your name</b>\n\n<i>Please reply with your name.</i>",
        parse_mode="HTML",
        reply_markup=markup
    )
    await state.set_state(UserBirthday.name)
    logger.debug("State set to UserBirthday.name")

#2
# NAME processing
async def process_name(message: types.Message, state: FSMContext):
    logger.info(f"Processing name input from user {message.from_user.id}")
    if not await check_authorization(message, state):
        return
    
    if message.text.startswith("/"):
        logger.warning("Name cannot be a command. Cancelling operation.")
        await message.reply(
            "<b>Operation cancelled</b>\n\n<i>Name cannot be a command</i>",
            parse_mode="HTML"
        )
        await state.clear()
        return

    logger.debug(f"Received name: {message.text}")
    await state.update_data(name=message.text)

    # Відправляємо повідомлення з запитом дати народження із кнопкою Cancel
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("❌ Cancel", callback_data="cancel"))

    await message.reply(
        "Please enter your birthdate (format: YYYY-MM-DD):",
        reply_markup=markup
    )
    await state.set_state(UserBirthday.birthdate)
    logger.debug("State set to UserBirthday.birthdate")

# 3
# DATE processing
async def process_birthdate(message: types.Message, state: FSMContext):
    logger.info(f"Processing birthdate input from user {message.from_user.id}")
    if not await check_authorization(message, state):
        return

    date_pattern = r"\d{4}-\d{2}-\d{2}"  # Регулярний вираз для дати формату YYYY-MM-DD
    if not re.fullmatch(date_pattern, message.text):
        logger.warning("Invalid date format received.")
        await message.reply(
            "<b>Operation cancelled</b>\n\n<b>Invalid date format.</b>\n\nPlease use the format: YYYY-MM-DD.",
            parse_mode="HTML"
        )
        await state.clear()
        return

    await state.update_data(birthdate=message.text)
    data = await state.get_data()
    name = data.get("name")
    birthdate = data.get("birthdate")
    logger.debug(f"Name: {name}, Birthdate: {birthdate}")

    await message.reply(
        f"✅ Thank you, {name}! Your birthdate is set as {birthdate}.",
        parse_mode="HTML"
    )
    await state.clear()

# Callback handler для скасування операції
async def cancel_handler(callback: types.CallbackQuery, state: FSMContext):
    logger.info(f"Received cancel callback from user {callback.from_user.id}")
    await callback.answer("Operation cancelled")
    # Редагуємо повідомлення, щоб прибрати інлайн-клавіатуру
    await callback.message.edit_reply_markup(reply_markup=None)
    await state.clear()
    logger.debug("Operation cancelled and state cleared.")

# Function to register handlers
def register_handlers(dp: Dispatcher):
    dp.message.register(start_command_handler, Command("start"))
    dp.message.register(help_command_handler, Command("help"))
    dp.message.register(new_birthday_handler, Command("new"))
    dp.message.register(process_name, StateFilter(UserBirthday.name))
    dp.message.register(process_birthdate, StateFilter(UserBirthday.birthdate))
    dp.callback_query.register(cancel_handler, F.data("cancel")) # F.data - helper
    logger.info("Handlers registered successfully.")
