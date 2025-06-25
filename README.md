# Telegram Birthday Greeting Bot

**Mixik** - Telegram bot

---

## PATCH NOTES v0.3 - 25.06.2025


#### Українська:

-   **Автоматичне створення директорії `data/`**: Бот тепер автоматично перевіряє та створює необхідну директорію для бази даних при запуску, забезпечуючи її надійну ініціалізацію.
-   **Спрощена архітектура бази даних `birthdays`**:
    -   Видалено окрему таблицю `birthday_persons`.
    -   Інформація про іменинника (ім'я або тег) тепер зберігається в одному текстовому полі **`birthday_person_identifier`** у таблиці `birthdays`, дозволяючи користувачам вводити ім'я або `@username`.
    -   Додано **`creator_telegram_user_id`** для чіткого визначення автора нагадування.
-   **Оптимізований процес додавання дня народження**:
    -   Спрощено процес `/new`, дозволяючи ввести ім'я або тег іменинника в одне поле.
    -   Покращено валідацію форматів дати (`YYYY-MM-DD` та `MM-DD`).
    -   Виправлено помилку `TypeError` при оновленні інформації про користувача.
-   **Інтеграція планувальника**: Додано запуск планувальника під час старту бота для автоматичного виконання фонових завдань, таких як перевірка днів народження.
-   **Покращене логування**: Розширено логування для відстеження процесів ініціалізації БД, реєстрації обробників та запуску планувальника.

#### English:

-   **Automatic `data/` Directory Creation**: The bot now automatically checks and creates the necessary database directory on startup, ensuring reliable initialization.
-   **Simplified `birthdays` Database Architecture**:
    -   The separate `birthday_persons` table has been removed.
    -   Honoree information (name or tag) is now stored in a single text field, **`birthday_person_identifier`**, within the `birthdays` table, allowing users to enter either a name or a @username.
    -   Added **`creator_telegram_user_id`** to clearly identify the reminder's author.
-   **Optimized Birthday Addition Process**:
    -   The `/new` command process has been streamlined, allowing entry of the honoree's name or tag in a single field.
    -   Date format validation has been improved to accept both `YYYY-MM-DD` and `MM-DD`.
    -   Fixed a `TypeError` encountered when updating user information.
-   **Scheduler Integration**: The scheduler is now launched during bot startup to automatically handle background tasks, such as checking for birthdays.
-   **Enhanced Logging**: Extended logging to better track database initialization, handler registration, and scheduler startup processes.

---

## PATCH NOTES v0.2 - 10.05.2025

#### Українська:

- **Скелет Step-Handler**: Впроваджено модульну логіку для послідовного збору інформації про день народження користувача.

- **Основні Команди**: Додано базові команди, такі як /start та /help, для початкової взаємодії з користувачем.

- **Перевірка Користувача**: Реалізовано механізм перевірки, щоб лише користувач-ініціатор міг продовжувати або скасовувати операцію, тим самим запобігаючи стороннім діям.

- **Адаптація для Високонавантажених Серверів**: Оптимізовано роботу бота для умов великої кількості одночасних користувачів.

- **Логування**: Додано розширене логування для покращення налагодження роботи та моніторингу процесів.

#### English:

- **Step-Handler Skeleton**: Introduce a modular step-handler framework for collecting birthday information.

- **Core Commands**: Add essential commands such as /start and /help for initial user interaction.

- **User Authorization**: Implement verification so that only the initiating (author) user can continue or cancel the operation, preventing unauthorized interruptions.

- **High-Concurrency Adaptation**: Adapt the bot to function reliably on high-traffic servers with many simultaneous users.

- **Logging**: Integrate detailed logging to assist in debugging and monitoring the system.

---

## PATCH NOTES v0.1 - 28.03.2025

#### Українська:

- **Початковий коміт**: Після ретельного аналізу було прийнято рішення змінити бібліотеку проєкту з Telebot на більш сучасну та гнучку Aiogram. Це дало можливість переосмислити логіку та структуру системи, запровадити асинхронний підхід та покращити масштабованість. У зв’язку з цим проєкт переписується з нуля, враховуючи нові вимоги та архітектурні принципи. Такий підхід дозволить забезпечити стабільність, продуктивність і більшу легкість у подальшому розвитку.

#### English:

- **Initial Commit**: After thorough analysis, a decision was made to replace the project's library from Telebot to the more modern and flexible Aiogram. This transition enables a complete rethinking of the system's logic and structure, adopting an asynchronous approach and improving scalability. As a result, the project is being rewritten from scratch, considering new requirements and architectural principles. This approach will ensure stability, performance, and greater ease for future development.

