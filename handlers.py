import re
from aiogram import F, Bot, Dispatcher, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


import config  # Import configuration
from logger import logger  # import logger

import database_manager

# Define states for user input
class UserBirthday(StatesGroup):
    name = State()
    birthdate = State()


# Хендлер для start функції
# Handler for the /start command
async def start_command_handler(message: types.Message):
    logger.info(f"Received /start from user {message.from_user.id}")
    await message.reply(config.START_MESSAGE, parse_mode="HTML")


# Хендлер для help функції
# Handler for the /help command
async def help_command_handler(message: types.Message):
    logger.info(f"Received /help from user {message.from_user.id}")
    await message.reply(config.COMMANDS_LIST, parse_mode="HTML")



async def is_user_authorized(message: types.Message, state: FSMContext) -> bool:    
    '''
    Допоміжна функція для перевірки, чи повідомлення надсилає користувач,який ініціював ланцюг введення даних
    Helper function to verify if the message is sent by the user who initiated the input sequence.
    '''
    
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

# TODO: повідомлення переглянути
# 1
async def new_birthday_handler(message: types.Message, state: FSMContext):
    '''
    Initializes the birthday registration process for a new birthday entry.
    This function is triggered by the '/new' command.

    Args:
        message (types.Message): The incoming Telegram message containing the name.
        state (FSMContext): The FSM context for the current user.
    '''

    logger.info(f"Initiating new birthday chain for user {message.from_user.id}")

    # Зберігаємо id користувача, який ініціював ланцюг
    await state.update_data(author_id=message.from_user.id)


    # -- Оновити або додати інформацію про чат -- 
    database_manager.add_or_update_chat_info(
        telegram_chat_id=message.chat.id,
        telegram_chat_name=message.chat.title if message.chat.title else message.from_user.full_name,
        telegram_chat_type=message.chat.type
    )


    # Створюємо inline-кнопку для скасування операції
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel")]
    ])

    bot_message = await message.reply(
        "<b>Введіть ім'я або тег користувача, чий день народження ви хочете додати до бази</b>\n\n<i>Будь ласка відповідайте на повідомлення.</i>\n<i>Please reply to this message.</i>",
        parse_mode="HTML",
        reply_markup=markup
    )

    # Зберігаємо ID повідомлення бота
    await state.update_data(last_bot_message_id=bot_message.message_id)

    # Переходимо до наступного етапу
    await state.set_state(UserBirthday.name)
    logger.debug("State set to UserBirthday.name")


#2
async def process_name(message: types.Message, state: FSMContext):
    '''
    Processes the user's telegram name or telegram tag input during the birthday registration flow.
    Saves the provided name in the FSM context.

    Args:
        message (types.Message): The incoming Telegram message containing the name.
        state (FSMContext): The FSM context for the current user.
    '''
    
    logger.info(f"Processing name input from user {message.from_user.id}")
    
    # canceling operation if user is not author
    if not await is_user_authorized(message, state):
        return
    
    
    # Зберігаємо введений текст "як є". Це буде наш ідентифікатор іменинника.
    birthday_person_identifier = message.text.strip()
    logger.debug(f"Received identifier: {birthday_person_identifier}")
    await state.update_data(birthday_person_identifier=birthday_person_identifier)

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
        "<b>Введіть дату, будь ласка. Формат: <code>YYYY-MM-DD (Рік-Місяць-День)</code></b>\n\n<i>Будь ласка відповідайте на повідомлення.</i>\n<i>Please reply to this message.</i>",
        parse_mode="HTML",
        reply_markup=markup # сюди присобачити кнопку
    )
    
    # Оновлюємо ID останнього повідомлення
    await state.update_data(last_bot_message_id=bot_message.message_id)

    # Переходимо до наступного етапу
    await state.set_state(UserBirthday.birthdate)
    logger.debug("State set to UserBirthday.birthdate")


# 3
async def process_birthdate(message: types.Message, state: FSMContext):
    '''
    Processes the user's birthdate input during the birthday registration flow.
    It validates the birthdate format, saves it to the FSM context, and then
    stores the full birthday entry (name and birthdate) into the database.

    Args:
        message (types.Message): The incoming Telegram message containing the name.
        state (FSMContext): The FSM context for the current user.
    '''

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
    birthday_person_identifier = data.get("birthday_person_identifier")
    birthdate = data.get("birthdate")
    logger.debug(f"birthday_person_identifier: {birthday_person_identifier}, birthdate: {birthdate}")

    creator_telegram_user_id = message.from_user.id
    creator_telegram_user_name = message.from_user.full_name
    creator_telegram_user_tag = message.from_user.username # ЯКЩО У КОРИСТУВАЧА НЕМАЄ ТЕГУ, ТО ПОЛЕ БУДЕ NONE

    chat_id_to_notify = message.chat.id

    # Інформація про того, хто додав день народження потрапляє у базу даних
    database_manager.add_or_update_user(
        telegram_user_id=creator_telegram_user_id, 
        telegram_user_name=creator_telegram_user_name, 
        telegram_user_tag=creator_telegram_user_tag
    )

    # Додаємо день народження в базу даних.
    database_manager.add_birthday_reminder(
        creator_telegram_user_id=creator_telegram_user_id,
        birthday_person_identifier=birthday_person_identifier,
        birthdate=birthdate,
        telegram_chat_id=chat_id_to_notify
    )


    # Надсилаємо відповідь
    await message.reply(
        f"✅ Дякую, {creator_telegram_user_name}! День народження користувача <code>{birthday_person_identifier}</code> збережено: <code>{birthdate}</code>.",
        parse_mode="HTML"
    )

    # Очищення стану та всіх тимчасових даних
    await state.clear()


async def list_birthdays(message: types.Message):
    """
    /list command handler to list all birthday reminders in the chat.
    """

    chat_id = message.chat.id
    logger.info(f"User {message.from_user.full_name} (id = {message.from_user.id}) requested /list command in chat {chat_id}")

    # дістати згадки з бази даних
    reminders = database_manager.get_birthday_reminder_for_chat(chat_id=chat_id)

    if not reminders:
        await message.reply("У цьому чаті ще немає доданих нагадувань про дні народження.")
        logger.info(f"No reminders found for chat {chat_id}.")
        return
    
    # Заголовок повідомлення
    initial_response_header = "🎂 **Ось усі нагадування про дні народження, додані для цього чату:**\n\n"
    
    # Список рядків для кожного запису у бд
    reminder_lines = []
    # У циклі перебираємо усі нагадування
    for i, reminder in enumerate(reminders): # enumerate додає індекс для кожного нагадування
        # Оновлене розпакування, щоб відповідало 7 полям із запиту
        # b.id, b.creator_telegram_user_id, b.birthday_person_identifier, b.birthdate, b.telegram_chat_id, c.telegram_chat_name, c.telegram_chat_type
        reminder_id, _, person_identifier, birthdate, _, _, _ = reminder # _ для ігнорування
        
        # Форматування дати для відображення
        display_date = birthdate
        if len(birthdate) == 10: # Якщо формат YYYY-MM-DD
            parts = birthdate.split('-')
            display_date = f"{parts[2]}.{parts[1]}.{parts[0]}" # DD.MM.YYYY
            # Або якщо рік не потрібен:
            # display_date = f"{parts[2]}.{parts[1]}" # DD.MM

        # Формується рядок
        reminder_lines.append(f"*{i+1}.* {person_identifier} - {display_date}, id = {reminder_id}\n")
    
    # --- ЛОГІКА РОЗБИТТЯ ПОВІДОМЛЕННЯ ---
    # Максимальна довжина повідомлення в Telegram (4096 символів)
    TELEGRAM_MESSAGE_LIMIT = 4096

    current_message_parts = [initial_response_header] # додаємо заголовок
    total_chars_in_current_message = len(initial_response_header) # рахуємо довжину заголовка
    sent_messages_count = 0 # лічильник відправлених повідомлень

    for line in reminder_lines:
        # Перевіряємо, чи додавання наступного рядка перевищить ліміт
        if total_chars_in_current_message + len(line) + 1 > TELEGRAM_MESSAGE_LIMIT: # кожен рядок потребує символу '/n' щоб не зливатись із попереднім

            # Якщо так, відправляємо поточне накопичене повідомлення
            await message.reply("".join(current_message_parts), parse_mode="Markdown")
            logger.debug(f"Sent part {sent_messages_count + 1} of list to chat {chat_id}.")
            sent_messages_count += 1 # оновлюємо лічильник
            
            # Починаємо нове повідомлення з нового рядка
            current_message_parts = [line] # затираємо стару змінну, додаючи повідомлення, що не помістилось на попередній сторінці
            total_chars_in_current_message = len(line)
        else:
            # Якщо ліміт не перевищено, додаємо рядок до поточного повідомлення
            current_message_parts.append(line)
            total_chars_in_current_message += len(line) + 1 # +1 для нового рядка
    
    # Відправляємо останнє накопичене повідомлення (якщо щось залишилось)
    if current_message_parts:
        await message.reply("".join(current_message_parts), parse_mode="Markdown")
        sent_messages_count += 1
        logger.debug(f"Sent final part {sent_messages_count} of list to chat {chat_id}.")

    logger.info(f"Successfully sent list of {len(reminders)} reminders in {sent_messages_count} messages to chat {chat_id}.")


async def delete_birthday_handler(message: types.Message, command: Command, bot: Bot): # command містить аргументи команди
    """
    Handles the /delete command to remove a birthday reminder from the database.

    This command requires a reminder ID (e.g., `/delete 123`).
    
    Only the reminder's creator or a chat administrator (in groups) can delete it.
    The bot will provide feedback for invalid IDs, permission issues, or successful deletion.
    """

    chat_id = message.chat.id
    user_id = message.from_user.id
    user_info = f"User {message.from_user.full_name} (id = {user_id})"
    
    logger.info(f"{user_info} requested /delete command in chat {chat_id}. Args: {command.args}")

    if not command.args:
        await message.reply(text="Будь ласка, вкажіть ID нагадування, яке потрібно видалити. Наприклад: <code>/delete 123</code>", parse_mode="HTML")
        return

    try:
        reminder_id_to_delete = int(command.args)
    except ValueError:
        await message.reply("ID нагадування має бути числом. Наприклад: `/delete 123`")
        return

    # 1. Перевірка, чи існує таке нагадування та хто його творець
    creator_id = database_manager.get_birthday_reminder_creator(reminder_id_to_delete)

    if creator_id is None:
        await message.reply(f"Нагадування з ID `{reminder_id_to_delete}` не знайдено.")
        logger.info(f"Attempt to delete non-existent reminder ID {reminder_id_to_delete} by {user_info}.")
        return

    # 2. Перевірка прав доступу
    can_delete = False
    
    # Якщо користувач є творцем запису
    if user_id == creator_id:
        can_delete = True
        logger.debug(f"{user_info} is the creator of reminder {reminder_id_to_delete}.")
    else:
        # Якщо це груповий чат, перевіряємо, чи користувач є адміністратором
        if message.chat.type in ["group", "supergroup"]:
            try:
                member = await bot.get_chat_member(chat_id, user_id)
                if member.status in ["creator", "administrator"]:
                    can_delete = True
                    logger.debug(f"{user_info} is an admin in group {chat_id}.")
                else:
                    logger.warning(f"{user_info} is not an admin in group {chat_id} and not creator of {reminder_id_to_delete}.")
            except Exception as e:
                logger.error(f"Error checking chat member status for {user_id} in chat {chat_id}: {e}", exc_info=True)
                await message.reply("Виникла помилка під час перевірки ваших прав адміністратора. Будь ласка, спробуйте пізніше.")
                return
        else: # Приватний чат, і користувач не творець
            logger.warning(f"{user_info} attempted to delete reminder {reminder_id_to_delete} in private chat without being creator.")

    if not can_delete:
        await message.reply("Ви не маєте прав видаляти це нагадування. Видалити його може лише той, хто його створив, або адміністратор цього чату (якщо це група).")
        return

    # 3. Видалення нагадування, якщо права підтверджені
    try:
        database_manager.delete_birthday_reminder(reminder_id_to_delete)
        
        await message.reply(f"Нагадування з ID `{reminder_id_to_delete}` успішно видалено.")
        logger.info(f"Reminder {reminder_id_to_delete} deleted by {user_info}.")
    except Exception as e:
        await message.reply(f"Не вдалося видалити нагадування з ID `{reminder_id_to_delete}`. Будь ласка, спробуйте ще раз або зверніться до підтримки.")
        logger.error(f"Failed to delete reminder {reminder_id_to_delete} by {user_info} - DB operation failed.")

    return


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
        text=f"⚠️ Користувач {callback.from_user.full_name} скасував операцію.",
        parse_mode="HTML"
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
    dp.message.register(list_birthdays, Command("list"))
    dp.message.register(delete_birthday_handler, Command("delete"))

    # Обробники станів FSM
    dp.message.register(process_name, StateFilter(UserBirthday.name))
    dp.message.register(process_birthdate, StateFilter(UserBirthday.birthdate))
    
    # Обробник для кнопки 'Cancel'
    dp.callback_query.register(cancel_handler, F.data == "cancel") # F.data - helper
