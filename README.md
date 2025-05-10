# Telegram Birthday Greeting Bot

**Mixik** - Telegram bot

---

## PATCH NOTES

### v0.2 - 10.05.2025

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

### v0.1 - 28.03.2025

#### Українська:

- **Початковий коміт**: Після ретельного аналізу було прийнято рішення змінити бібліотеку проєкту з Telebot на більш сучасну та гнучку Aiogram. Це дало можливість переосмислити логіку та структуру системи, запровадити асинхронний підхід та покращити масштабованість. У зв’язку з цим проєкт переписується з нуля, враховуючи нові вимоги та архітектурні принципи. Такий підхід дозволить забезпечити стабільність, продуктивність і більшу легкість у подальшому розвитку.

#### English:

- **Initial Commit**: After thorough analysis, a decision was made to replace the project's library from Telebot to the more modern and flexible Aiogram. This transition enables a complete rethinking of the system's logic and structure, adopting an asynchronous approach and improving scalability. As a result, the project is being rewritten from scratch, considering new requirements and architectural principles. This approach will ensure stability, performance, and greater ease for future development.

