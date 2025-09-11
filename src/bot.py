import logging

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackContext

# Replace with your bot token and channel ID
BOT_TOKEN = '7704927071:AAHKCk5wR6dTwi05JMGnfvcjmHs4lk_bXBo'
MAIN_CHANNEL_ID = '-1002875748532'  # Use the channel username or channel ID

user_ids = set()
logging.basicConfig(filename='ships.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')


# Define a few command handlers. These usually take the two arguments update and
# context.


# Start: add user to list of tracked users.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    logging.info("User {user.mention_html()}, id {user.id} joined.")
    user_ids.add(update.message.from_user.id)
    await update.message.reply_html(
        rf"Добро пожаловать на борт, капитан {user.mention_html()}! Новые корабли будут пересланы в этот чат. Также они доступны на канале t.me/clear_ships"
    )

# Stop: remove user from list of tracked users.
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    logging.info("User {user.mention_html()}, id {user.id} left.")
    user_ids.remove(update.message.from_user.id)
    await update.message.reply_html(
        rf"Вы отписаны от дальнейших сообщений. Чтобы снова включить обновления в этом чате, используйте команду /start. Ваши сообщения боту продолжат появляться на канале t.me/clear_ships"
    )

async def forward_ship(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Forward the ship to the main channel
    await context.bot.send_message(chat_id=MAIN_CHANNEL_ID, text=update.message.text)
    logging.info("User {user.mention_html()}, id {user.id} sent message: {update.message.text} ")

    for user_id in user_ids:
        try:
            if (user_id !=user.id):
                await context.bot.send_message(chat_id=user_id, text=update.message.text)
        except Exception as e:
            logging.debug(f"Could not send message to {user_id}: {e}")
            print(f"Could not send message to {user_id}: {e}")

#async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#    await update.message.reply_text("Help!")


def main() -> None:
    # Starting the harbor...

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(BOT_TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))
    #application.add_handler(CommandHandler("help", help_command))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_ship))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    """Harbor started"""

if __name__ == '__main__':
    main()
                                    