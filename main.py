import json
import re
from telegram import (
    Update, KeyboardButton, ReplyKeyboardMarkup, Contact
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, ConversationHandler, filters
)
from config import BOT_TOKEN

USERS_FILE = "users.json"
ASK_AUTH_METHOD, RECEIVE_DATA = range(2)

# ========= Хранилище =========
def save_user(telegram_id, full_name, bin_number=None, phone_number=None):
    try:
        with open(USERS_FILE, "r") as f:
            users = json.load(f)
    except FileNotFoundError:
        users = {}

    users[str(telegram_id)] = {
        "name": full_name,
        "bin": bin_number,
        "phone": phone_number
    }

    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

def user_is_authenticated(telegram_id):
    try:
        with open(USERS_FILE, "r") as f:
            users = json.load(f)
            user = users.get(str(telegram_id))
            return user and (user.get("phone") or user.get("bin"))
    except FileNotFoundError:
        return False

def get_user_data(telegram_id):
    try:
        with open(USERS_FILE, "r") as f:
            users = json.load(f)
            return users.get(str(telegram_id))
    except FileNotFoundError:
        return None

# ========= Валидация =========
def is_valid_phone(phone: str) -> bool:
    return bool(re.fullmatch(r"\+77\d{9}", phone))

def is_valid_bin(bin_code: str) -> bool:
    return bool(re.fullmatch(r"\d{12}", bin_code))

# ========= Хендлеры =========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    telegram_id = user.id
    full_name = user.full_name

    context.user_data["telegram_id"] = telegram_id
    context.user_data["full_name"] = full_name

    await update.message.reply_text(f"{full_name}, Вас приветствует Баланс-1! 👋")

    if user_is_authenticated(telegram_id):
        await update.message.reply_text("Вы уже авторизованы ✅")
        return ConversationHandler.END

    reply_markup = ReplyKeyboardMarkup(
        [
            [KeyboardButton("📞 Телефон", request_contact=True)],
            [KeyboardButton("🏢 БИН")],
            [KeyboardButton("📄 Мой статус")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await update.message.reply_text(
        "Вы не авторизованы.\nВыберите способ авторизации:",
        reply_markup=reply_markup
    )
    return ASK_AUTH_METHOD

async def ask_for_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if message.contact:
        phone = message.contact.phone_number
        if not is_valid_phone(phone):
            await update.message.reply_text("❌ Неверный номер. Используйте формат +77XXXXXXXXX.")
            return ASK_AUTH_METHOD
        save_user(context.user_data["telegram_id"], context.user_data["full_name"], phone_number=phone)
        await update.message.reply_text("✅ Контакт сохранён.")
        return ConversationHandler.END

    elif message.text == "🏢 БИН":
        context.user_data["auth_method"] = "bin"
        await update.message.reply_text("Пожалуйста, введите БИН вашей компании:")
        return RECEIVE_DATA

    elif message.text == "📞 Телефон":
        context.user_data["auth_method"] = "phone"
        await update.message.reply_text("Введите номер телефона в формате +77XXXXXXXXX:")
        return RECEIVE_DATA

    elif message.text == "📄 Мой статус":
        user_data = get_user_data(context.user_data["telegram_id"])
        if not user_data:
            await update.message.reply_text("Вы ещё не проходили авторизацию.")
            return ASK_AUTH_METHOD
        bin_info = user_data.get("bin") or "—"
        phone_info = user_data.get("phone") or "—"
        await update.message.reply_text(
            f"👤 Ваши данные:\nИмя: {user_data['name']}\nТелефон: {phone_info}\nБИН: {bin_info}"
        )
        return ASK_AUTH_METHOD

    else:
        await update.message.reply_text("Пожалуйста, выберите Телефон или БИН.")
        return ASK_AUTH_METHOD

async def receive_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    telegram_id = context.user_data["telegram_id"]
    full_name = context.user_data["full_name"]
    auth_method = context.user_data["auth_method"]

    if auth_method == "phone":
        if not is_valid_phone(user_input):
            await update.message.reply_text("❌ Неверный формат номера. Введите +77XXXXXXXXX:")
            return RECEIVE_DATA
        save_user(telegram_id, full_name, phone_number=user_input)

    elif auth_method == "bin":
        if not is_valid_bin(user_input):
            await update.message.reply_text("❌ БИН должен содержать 12 цифр.")
            return RECEIVE_DATA
        save_user(telegram_id, full_name, bin_number=user_input)

    await update.message.reply_text("✅ Спасибо! Мы сохранили ваши данные.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Авторизация отменена.")
    return ConversationHandler.END

# ========= Запуск =========
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_AUTH_METHOD: [MessageHandler(filters.ALL & ~filters.COMMAND, ask_for_input)],
            RECEIVE_DATA: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_data)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(conv_handler)

    print("Бот запущен ✅")
    app.run_polling()