import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

USERS_FILE = "users.json"

# Функция для сохранения Telegram ID в файл
def save_user(telegram_id, full_name):
    try:
        with open(USERS_FILE, "r") as f:
            users = json.load(f)
    except FileNotFoundError:
        users = {}

    users[str(telegram_id)] = {"name": full_name}

    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

# Хендлер команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    telegram_id = user.id
    full_name = user.full_name

    # Сохраняем
    save_user(telegram_id, full_name)

    await update.message.reply_text(
        f"{full_name}, Вас приветсвует Баланс-1! 👋\nВаш Telegram ID: {telegram_id}"
    )

# Запуск бота
if __name__ == "__main__":
    app = ApplicationBuilder().token("7767298614:AAGqfU6XrROuljuqDDakRmmIfDEnC5USkzU").build()
    app.add_handler(CommandHandler("start", start))
    print("Бот запущен ✅")
    app.run_polling()
