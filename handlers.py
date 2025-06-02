import re
from aiogram import F, Dispatcher, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


import config  # Import configuration
from logger import logger  # import logger


# Define states for user input
class UserBirthday(StatesGroup):
    name = State()
    birthdate = State()


# Хендлер для start функції
# Handler for the /start command
async def start_command_handler(message: types.Message):
    logger.info(f"Received /start from user {message.from_user.id}")
    await message.reply(config.startMessage, parse_mode="HTML")


# Хендлер для help функції
# Handler for the /help command
async def help_command_handler(message: types.Message):
    logger.info(f"Received /help from user {message.from_user.id}")
    await message.reply(config.commandsList, parse_mode="HTML")



# Допоміжна функція для перевірки, чи повідомлення надсилає користувач,який ініціював ланцюг введення даних
# Helper function to verify if the message is sent by the user who initiated the input sequence.
async def is_user_authorized(message: types.Message, state: FSMContext) -> bool:    
    
    # Ensure the user is replying to the bot's message
    if not message.reply_to_message or message.reply_to_message.from_user.id != message.bot.id:
        
        # logger.warning(f"Message from user {message.from_user.id} is not a reply to the bot. Ignoring.")
        return False  # Ignore the message if it is not a reply

    # Verify if the message sender is the one who initiated the interaction
    data = await state.get_data()
    author_id = data.get("author_id")
    
    # If no author is stored, allow other users input data
    if author_id is None:
        
        logger.debug("No author_id found in state. Allowing operation.")
        return True
    
    # Ignore responses from other users
    if message.from_user.id != author_id:
        
        logger.warning(f"Unauthorized access attempt by user {message.from_user.id}. Expected {author_id}.")
        return False  
    
    # Prevent commands from being processed during the interaction
    if message.text.startswith("/"):
        
        logger.warning(f"Command input detected from user {message.from_user.id}. Operation cancelled.")
        await message.reply(
            "<b>Operation cancelled</b>\n\n<i>Commands are not allowed during this operation.</i>",
            parse_mode="HTML"
        )
        return False

    # Якщо всі перевірки пройдені, операція продовжується
    # If all of the checks were passed - continue
    logger.debug("User authorization passed.")
    return True


# FSM (Finite State Machine) - дозволяє контролювати стани користувача в чаті


# 1
# /new – start commands chain
async def new_birthday_handler(message: types.Message, state: FSMContext):
    
    logger.info(f"Initiating new birthday chain for user {message.from_user.id}")

    # Зберігаємо id користувача, який ініціював ланцюг
    await state.update_data(author_id=message.from_user.id)

    # Створюємо inline-кнопку для скасування операції
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel")]
    ])

    bot_message = await message.reply(
        "<b>Enter your name</b>\n\n<i>Будь ласка відповідайте на повідомлення.</i>\n<i>Please reply to this message.</i>",
        parse_mode="HTML",
        reply_markup=markup
    )

    # Зберігаємо ID повідомлення бота
    await state.update_data(last_bot_message_id=bot_message.message_id)

    # Переходимо до наступного етапу
    await state.set_state(UserBirthday.name)
    logger.debug("State set to UserBirthday.name")





#2
# NAME processing
async def process_name(message: types.Message, state: FSMContext):
    
    logger.info(f"Processing name input from user {message.from_user.id}")
    
    # canceling operation if user is not author
    if not await is_user_authorized(message, state):
        return
    
    logger.debug(f"Received name: {message.text}")
    await state.update_data(name=message.text)


    # Отримуємо ID попереднього повідомлення
    data = await state.get_data()
    last_bot_message_id = data.get("last_bot_message_id")

    # Видаляємо кнопки з попереднього повідомлення
    if last_bot_message_id:
        await message.bot.edit_message_reply_markup(
            chat_id=message.chat.id,
            message_id=last_bot_message_id,
            reply_markup=None
        )


    # Кнопка Cancel
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel")]
    ])

    # Відправляємо повідомлення з запитом дати народження із кнопкою Cancel
    bot_message = await message.reply(
        "<b>Please enter your birthdate (format: YYYY-MM-DD):</b>\n\n<i>Будь ласка відповідайте на повідомлення.</i>\n<i>Please reply to this message.</i>",
        reply_markup=markup # сюди присобачити кнопку
    )

    
    # Оновлюємо ID останнього повідомлення
    await state.update_data(last_bot_message_id=bot_message.message_id)


    # Переходимо до наступного етапу
    await state.set_state(UserBirthday.birthdate)
    logger.debug("State set to UserBirthday.birthdate")





# 3
# DATE processing
async def process_birthdate(message: types.Message, state: FSMContext):
    
    logger.info(f"Processing birthdate input from user {message.from_user.id}")
    if not await is_user_authorized(message, state):
        return

    # Update Data in FSM
    await state.update_data(birthdate=message.text)

    # Отримуємо ID попереднього повідомлення
    data = await state.get_data()
    last_bot_message_id = data.get("last_bot_message_id")

    # Видаляємо кнопки з попереднього повідомлення
    if last_bot_message_id:
        await message.bot.edit_message_reply_markup(
            chat_id=message.chat.id,
            message_id=last_bot_message_id,
            reply_markup=None
        )


    date_pattern = r"\d{4}-\d{2}-\d{2}"  # Регулярний вираз для дати формату YYYY-MM-DD
    if not re.fullmatch(date_pattern, message.text):
        logger.warning("Invalid date format received.")
        await message.reply(
            "<b>Operation cancelled</b>\n\n<b>Invalid date format.</b>\n\nPlease use the format: YYYY-MM-DD.",
            parse_mode="HTML"
        )
        await state.clear()
        return


    # Дістаємо дані про користувача
    name = data.get("name")
    birthdate = data.get("birthdate")
    logger.debug(f"Name: {name}, Birthdate: {birthdate}")



    # TODO: тут потрібно буде обробити це все і подати дані в БД
    # ADD DATABASE HANDLERS



    await message.reply(
        f"✅ Thank you, {name}! Your birthdate is set as {birthdate}.",
        parse_mode="HTML"
    )

    # Очищення стану та всіх тимчасових даних
    await state.clear()


# Callback handler для скасування операції
async def cancel_handler(callback: types.CallbackQuery, state: FSMContext):
    
    # Дістати дані юзера
    # Get user_id data
    data = await state.get_data()
    author_id = data.get("author_id")

    # Перевірити чи автор команди намагається скасувати операцію
    # Check attempt, if the command author trying to cancel operation
    if callback.from_user.id != author_id:
        logger.warning(f"Unauthorized cancel attempt by user {callback.from_user.id}")
        await callback.answer("❌ You are not allowed to cancel this operation.")
        return

    logger.info(f"Received cancel callback from user {callback.from_user.id}")
    
    # Сповіщення, що користувач скасував операцію
    await callback.answer("Operation cancelled")

    # Сповіщення в чат про скасування операції
    # Send a notification to the chat about cancellation
    await callback.bot.send_message(
        chat_id=callback.message.chat.id,
        text=f"⚠️ User {callback.from_user.full_name} has cancelled the operation."
    )
    
    # Редагуємо повідомлення, щоб прибрати інлайн-клавіатуру
    await callback.message.edit_reply_markup(reply_markup=None)
    
    await state.clear()
    
    logger.debug("Operation cancelled and state cleared.")






# Реєструємо всі ці функції
# Function to register handlers
def register_handlers(dp: Dispatcher):
    dp.message.register(start_command_handler, Command("start"))
    dp.message.register(help_command_handler, Command("help"))
    dp.message.register(new_birthday_handler, Command("new"))
    dp.message.register(process_name, StateFilter(UserBirthday.name))
    dp.message.register(process_birthdate, StateFilter(UserBirthday.birthdate))
    dp.callback_query.register(cancel_handler, F.data == "cancel") # F.data - helper
    logger.info("Handlers registered successfully.")
