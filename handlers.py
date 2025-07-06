from admin import notify_admins
from telegram import (
    Update, KeyboardButton, ReplyKeyboardMarkup
)
from telegram.ext import (
    ContextTypes, ConversationHandler, MessageHandler, filters
)
from validation import is_valid_phone, is_valid_bin
from storage import (
    save_user, get_user_data,
    remove_user, user_is_authenticated
)
from states import ASK_AUTH_METHOD, RECEIVE_DATA

reply_markup_auth = ReplyKeyboardMarkup(
    [
        [KeyboardButton("📄 Мой статус")],
        [KeyboardButton("📩 Оставить заявку")],
        [KeyboardButton("🔁 Сбросить авторизацию")]
    ],
    resize_keyboard=True
)

reply_markup_unauth = ReplyKeyboardMarkup(
    [
        [KeyboardButton("📞 Телефон")],
        [KeyboardButton("🏢 БИН")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

reply_markup_phone_choice = ReplyKeyboardMarkup(
    [
        [KeyboardButton("📲 Отправить мой номер", request_contact=True)],
        [KeyboardButton("✍ Ввести вручную")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    telegram_id = user.id
    full_name = user.full_name

    context.user_data["telegram_id"] = telegram_id
    context.user_data["full_name"] = full_name

    await update.message.reply_text(f"{full_name}, Вас приветствует Баланс-1! 👋")

    if user_is_authenticated(telegram_id):
        await update.message.reply_text(
            "Вы уже авторизованы ✅\nВыберите одну из доступных команд.",
            reply_markup=reply_markup_auth
        )
    else:
        await update.message.reply_text(
            "Вы не авторизованы.\nВыберите способ авторизации:",
            reply_markup=reply_markup_unauth
        )

    await update.message.reply_text(
        "ℹ️ *Доступные команды:*\n"
        "/status — проверить статус\n"
        "/reset — сбросить авторизацию",
        parse_mode="Markdown"
    )
    return ASK_AUTH_METHOD


async def ask_for_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    telegram_id = context.user_data.get("telegram_id") or message.from_user.id
    full_name = context.user_data.get("full_name") or message.from_user.full_name

    if message.text == "📞 Телефон":
        context.user_data["auth_method"] = "phone_choice"
        await message.reply_text(
            "Вы хотите отправить свой номер из Telegram или ввести вручную?",
            reply_markup=reply_markup_phone_choice
        )
        return ASK_AUTH_METHOD

    elif message.contact:
        phone = message.contact.phone_number
        if not is_valid_phone(phone):
            await message.reply_text("❌ Неверный номер. Используйте формат +77XXXXXXXXX.")
            return ASK_AUTH_METHOD

        save_user(telegram_id, full_name, phone_number=phone)
        await notify_admins(context, full_name, telegram_id, phone=phone)
        await message.reply_text("✅ Спасибо! Вы успешно авторизованы.", reply_markup=reply_markup_auth)
        return ConversationHandler.END

    elif message.text == "✍ Ввести вручную":
        context.user_data["auth_method"] = "phone"
        await message.reply_text("Введите номер телефона в формате +77XXXXXXXXX:")
        return RECEIVE_DATA

    elif message.text == "🏢 БИН":
        context.user_data["auth_method"] = "bin"
        await message.reply_text("Пожалуйста, введите БИН вашей компании:")
        return RECEIVE_DATA

    elif message.text == "📄 Мой статус":
        user_data = get_user_data(telegram_id)
        if not user_data or (not user_data.get("phone") and not user_data.get("bin")):
            await message.reply_text("Вы ещё не авторизованы.")
        else:
            bin_info = user_data.get("bin") or "—"
            phone_info = user_data.get("phone") or "—"
            await message.reply_text(
                f"👤 Вы авторизованы.\nИмя: {user_data['name']}\nТелефон: {phone_info}\nБИН: {bin_info}"
            )
        return ASK_AUTH_METHOD

    elif message.text == "📩 Оставить заявку":
        if user_is_authenticated(telegram_id):
            await notify_admins(context, full_name, telegram_id, is_request=True)
            await message.reply_text("📨 Ваша заявка отправлена менеджеру.")
        else:
            await message.reply_text("❌ Вы не авторизованы. Сначала авторизуйтесь.")
        return ASK_AUTH_METHOD

    elif message.text == "🔁 Сбросить авторизацию":
        if remove_user(telegram_id):
            await message.reply_text("🔁 Ваши данные удалены. Вы не авторизованы.", reply_markup=reply_markup_unauth)
        else:
            await message.reply_text("ℹ️ У вас не было сохранённых данных.")
        return ASK_AUTH_METHOD

    else:
        await message.reply_text("Пожалуйста, выберите действие из доступных.")
        return ASK_AUTH_METHOD


async def receive_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    telegram_id = context.user_data["telegram_id"]
    full_name = context.user_data["full_name"]
    auth_method = context.user_data["auth_method"]

    if auth_method == "phone":
        if not is_valid_phone(user_input):
            await update.message.reply_text("❌ Неверный формат номера. Попробуйте выбрать опцию 'Ввести вручную' и введите номер в формате +77XXXXXXXXX:")
            return RECEIVE_DATA
        save_user(telegram_id, full_name, phone_number=user_input)
        await notify_admins(context, full_name, telegram_id, phone=user_input)

    elif auth_method == "bin":
        if not is_valid_bin(user_input):
            await update.message.reply_text("❌ БИН должен содержать 12 цифр.")
            return RECEIVE_DATA
        save_user(telegram_id, full_name, bin_number=user_input)
        await notify_admins(context, full_name, telegram_id, bin_code=user_input)

    await update.message.reply_text("✅ Спасибо! Вы успешно авторизованы.", reply_markup=reply_markup_auth)
    return ConversationHandler.END

async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    telegram_id = update.effective_user.id
    full_name = update.effective_user.full_name

    if text == "📄 Мой статус":
        user_data = get_user_data(telegram_id)
        if not user_data or (not user_data.get("phone") and not user_data.get("bin")):
            await update.message.reply_text("Вы ещё не авторизованы.")
        else:
            bin_info = user_data.get("bin") or "—"
            phone_info = user_data.get("phone") or "—"
            await update.message.reply_text(f"👤 Вы авторизованы.\nИмя: {user_data['name']}\nТелефон: {phone_info}\nБИН: {bin_info}")

    elif text == "📩 Оставить заявку":
        if user_is_authenticated(telegram_id):
            await notify_admins(context, full_name, telegram_id, is_request=True)
            await update.message.reply_text("📨 Ваша заявка отправлена менеджеру.")
        else:
            await update.message.reply_text("❌ Вы не авторизованы. Сначала авторизуйтесь.")

    elif text == "🔁 Сбросить авторизацию":
        if remove_user(telegram_id):
            await update.message.reply_text("🔁 Ваши данные удалены. Вы не авторизованы.")
        else:
            await update.message.reply_text("ℹ️ У вас не было сохранённых данных.")


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    user_data = get_user_data(telegram_id)

    if not user_data or (not user_data.get("phone") and not user_data.get("bin")):
        await update.message.reply_text("Вы ещё не авторизованы.")
    else:
        bin_info = user_data.get("bin") or "—"
        phone_info = user_data.get("phone") or "—"
        await update.message.reply_text(
            f"👤 Вы авторизованы.\nИмя: {user_data['name']}\nТелефон: {phone_info}\nБИН: {bin_info}"
        )


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    if remove_user(telegram_id):
        await update.message.reply_text("🔁 Ваши данные удалены. Вы не авторизованы.", reply_markup=reply_markup_unauth)
    else:
        await update.message.reply_text("ℹ️ У вас не было сохранённых данных.")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Авторизация отменена.")
    return ConversationHandler.END