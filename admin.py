ADMINS = [
    123456789, 
    987654321
]

def is_admin(user_id: int) -> bool:
    return user_id in ADMINS

async def notify_admins(context, full_name, telegram_id, phone=None, bin_code=None):
    parts = [
        "📥 *Новая заявка на авторизацию*\n",
        f"👤 Имя: {full_name}",
        f"🆔 Telegram ID: {telegram_id}",
    ]
    if phone:
        parts.append(f"📞 Телефон: {phone}")
    if bin_code:
        parts.append(f"🏢 БИН: {bin_code}")

    message = "\n".join(parts)

    for admin_id in ADMINS:
        try:
            await context.bot.send_message(chat_id=admin_id, text=message, parse_mode="Markdown")
        except Exception as e:
            print(f"Ошибка при отправке админу {admin_id}: {e}")
