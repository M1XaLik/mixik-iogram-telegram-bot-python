from aiogram import Dispatcher, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

import config  # Import configurations

# Define states for user input
class UserBirthday(StatesGroup):
    name = State()
    birthdate = State()

# Handler for the /start command
async def start_command_handler(message: types.Message):
    await message.reply(config.startMessage, parse_mode="HTML")

# Handler for the /help command
async def help_command_handler(message: types.Message):
    await message.reply(config.commandsList, parse_mode="HTML")

# Handler for the /new command to start user input
async def new_birthday_handler(message: types.Message, state: FSMContext):
    await message.reply("👋 Please enter your name:")
    await state.set_state(UserBirthday.name)

# Handling user input for name
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.reply("📅 Great! Now enter your birthdate (format: YYYY-MM-DD):")
    await state.set_state(UserBirthday.birthdate)

# Handling user input for birthdate
async def process_birthdate(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    name = user_data.get("name")
    birthdate = message.text
    
    await message.reply(f"✅ Thank you, {name}! Your birthdate is set to {birthdate}.")
    await state.clear()

# Function to register handlers
def register_handlers(dp: Dispatcher):
    dp.message.register(start_command_handler, Command("start"))
    dp.message.register(help_command_handler, Command("help"))
    dp.message.register(new_birthday_handler, Command("new"))
    dp.message.register(process_name, StateFilter(UserBirthday.name))
    dp.message.register(process_birthdate, StateFilter(UserBirthday.birthdate))
