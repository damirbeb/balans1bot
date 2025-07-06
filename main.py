from telegram.ext import (
    ApplicationBuilder, CommandHandler, ConversationHandler, MessageHandler, filters
)
from config import BOT_TOKEN
from handlers import (
    start, ask_for_input, receive_data, handle_main_menu,
    status_command, reset_command, cancel
)
from states import ASK_AUTH_METHOD, RECEIVE_DATA

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
    app.add_handler(MessageHandler(
        filters.TEXT & (~filters.COMMAND),
        handle_main_menu
    ))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("reset", reset_command))

    print("Бот запущен ✅")
    app.run_polling()