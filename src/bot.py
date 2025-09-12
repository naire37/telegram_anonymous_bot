import logging
import os
import argparse

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv


formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')


def setup_logger(name, log_file, level=logging.INFO):
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)
    current_logger = logging.getLogger(name)
    current_logger.setLevel(level)
    current_logger.addHandler(handler)
    return current_logger


# General app logger
logger = setup_logger('general', 'logs/ships.log')

# Users log, until I can implement a DB

# logging.basicConfig(filename='logs/ships.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger("telegram_anonymous_bot")


def get_bot_token() -> str:
    # Check, which environment the script is running for; default to DEV.
    environment = "DEV"
    available_env = ["DEV", "PROD", "OFFTOP"]
    printable_view_of_available_env = ", ".join(available_env)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--env", help="Environment, for which to run the script: " + printable_view_of_available_env)
    args = parser.parse_args()
    if args.env is not None:
        if args.env in available_env:
            environment = args.env
            global logger
            logger = setup_logger('general', 'logs/ships_' + args.env +'.log')
            global user_logger
            user_logger = setup_logger('user_logger', 'logs/users_' + args.env +'.log')
        else:
            logger.error(f"Environment '{args.env}' not found in the list.")
    else:
        logger.info("Environment was not provided, defaulting to DEV.")

    # Load the configuration based on environment above. Configuration is stored in .env file.
    load_dotenv()
    bot_token = os.getenv('BOT_TOKEN_' + environment)
    # logger.info(f"Bot token {bot_token} used.")
    return bot_token or 'DEV'


# TBD: store users in a DB.
user_ids = set()


# /start:
#  - add user to list of tracked users (TBD: store this in DB!)
#  - print some kind of welcoming message
#  - TBD: print help message (store as a constant)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if (user is not None):
        user_logger.info(f"User {user.mention_html()}, id {user.id} joined.")
        user_ids.add(user.id)
        if (update.message is not None):
            await update.message.reply_html(
                rf"Добро пожаловать на борт, капитан {user.mention_html()}! Это канал для анонимной ролевой игры. Пожалуйста, избегайте сообщений о реале. Канал в разработке."
            )

# /stop:
#  - remove user from list of tracked users (TBD: update DB!)
#  - print some kind of farewell message
#  - TBD: clear history so that they can't write to bot again
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if (user is not None):
        user_logger.info("User {user.mention_html()}, id {user.id} left.")
        if (user.id in user_ids):
            user_ids.remove(user.id)
        if (update.message is not None):
            await update.message.reply_html(
                rf"Вы отписаны от дальнейших сообщений. Чтобы снова включить обновления в этом чате, используйте команду /start."
            )


async def dispatch_to_all(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # await context.bot.send_message(chat_id=MAIN_CHANNEL_ID, text=update.message.text)
    logger.info(
        f"User {user.mention_html()}, id {user.id} sent message: {update.message.text} ")

    for user_id in user_ids:
        try:
            if (user_id != update.message.from_user.id):
                await context.bot.send_message(chat_id=user_id, text=update.message.text)
        except Exception as e:
            logging.debug(f"Could not send message to {user_id}: {e}")
            print(f"Could not send message to {user_id}: {e}")

# async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#    await update.message.reply_text("Help!")


def main() -> None:
    # Starting the harbor...
    bot_token = get_bot_token()

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(bot_token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))
    # application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, dispatch_to_all))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
