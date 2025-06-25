import os
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

# Receive Token
BOT_TOKEN = os.getenv("TOKEN")

# Отримуємо абсолютний шлях до файлу бази даних (потрібно для ініціалізації БД)
DB_DIR = ".data" # Папка для бази даних (шлях)
DB_NAME = "botbase.db"
DB_PATH = os.path.join(DB_DIR, DB_NAME)

# -- SCHEDULER (Змінні для планувальника) --

# Час, коли бот буде перевіряти дні народження та надсилати нагадування
# Зазвичай це час, коли більшість людей вже прокинулися, але ще не пізно.
# Приклад: 1:00 ночі
BIRTHDAY_REMINDER_HOUR = 1
BIRTHDAY_REMINDER_MINUTE = 0

# Максимальний час (у секундах), протягом якого завдання може бути виконане,
# якщо воно було пропущено через перезапуск бота або іншу проблему.
# Наприклад, якщо бот перезапустився о 9:05, а завдання мало запуститися о 9:00,
# і misfire_grace_time=300 (5 хвилин), то завдання все одно буде виконане.
# Якщо 0, то пропущене завдання не буде виконано.
SCHEDULER_MISFIRE_GRACE_TIME = 300 # 5 хвилин (300 секунд)

# Часова зона в якій буде запускатися бот
SCHEDULER_TIMEZONE = 'Europe/Kiev'


# Початкове повідомлення
START_MESSAGE = "Привіт😊\nДля отримання розширеної інформації скористайся командою 👉🏿 <b>/help</b>"

# HELP 
COMMANDS_LIST = (
    "<b>🛠COMMANDS🎭</b> \n\n" 
    "• <b>/help</b> - <i>список команд та інформації по них</i> \n\n" 
    "• <b>/new</b> - <i>додати нову згадку про день народження</i> \n\n"
    "• <b>/list</b> - <i>вивести список днів народження</i> \n\n"
    "• <b>/delete</b> - <i>видалити день народження із бази даних\nПримітка:\nдля коректної роботи використовуйте команду <code>/delete [id]</code> - де параметр \"id\" є порядковим номером запису\n(усі записи чату можна переглянути за допомогою команди <code>/list</code>) </i>\n\n"
)

# RANDOM BIRTHDAY GIFS 
BIRTHDAY_GIFS = [
   #Fudzivara dance
   'https://media.giphy.com/media/RLJxQtX8Hs7XytaoyX/giphy.gif',
   #Chuck Noris
   'https://media.giphy.com/media/oBPOP48aQpIxq/giphy.gif',
   #Clapping Applause GIF By The Gentlemen
   'https://media.giphy.com/media/WUmwGKySIjs8L7oYn9/giphy.gif',
   #Gentlemen open the car
   'https://media.giphy.com/media/XE7HOP9gIzwik3ND6F/giphy.gif',
   #DIKAPRIO HEAD MOVEMENT
   'https://media.giphy.com/media/yprjFmpQnihhRZvHv0/giphy.gif',
   #THE LEGEND: flovers
   'https://media.giphy.com/media/b26xrSmDzn5fO/giphy.gif',
   #DRUNK musician
   'https://media.giphy.com/media/3ohzdHa8nODi4IWIww/giphy.gif',
   #SCREAM wazzap
   'https://media.giphy.com/media/101DNxoBTatF16/giphy.gif'
]

# TEXTS
BIRTHDAY_TEXTS = [
    "Вітаю, щастя здоров'я тобі бажаю, щоб ніколи не було запору, щоб все йшло по плану, а не по пезді. Хай завжди все виходить у тебе і хай фортуна ніколи не повертається до тебе дупою.",
    "Вітаю, щастя, здоров'я, многая літа, діточок як на небі зірочок, щоб всі бажання збувались, щоб все в тебе було і нічого за це тобі не було, щоб песос стояв і серце билось.",
    # "Якщо щось згадаю, то напишу...",
    "Вітаю тебе із днем народження, щоб в цей день твоя найжаданіша мрія здійснилася, щоб ніколи на довго не затримувалася чорна смужка в твоєму житті, щоб не забував(ла) про важливі плани й рідних. Нехай кожний день принесе тобі незабутні враження, щоб цінував(ла) кожен момент в своєму житті ну і здоров'я, його не вернеш.",
    "200 гривень",
    f"З Днем народження!!! 🎊🎂🎈🎊 Всього найкращого 🥳🥳🥳"
]

# WHEN SOMETHING IS UNAVALIABLE BOT WILL SEND THIS 
NO_GIFS = [
    #Hunnem no
    'https://media.giphy.com/media/YPDm9ybXqDLNB9XL3T/giphy.gif',
    #Hunnem turns
    'https://media.giphy.com/media/QYXltyeyluyvfKwfxU/giphy.gif'
]