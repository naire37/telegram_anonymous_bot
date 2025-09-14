import logging
import os
import argparse
import csv
import os.path
import time
from datetime import datetime

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv


# TBD: global vars are evil, but this is a first pass.
users = []
environment = "DEV"

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

def setup_logger(name, log_file, level=logging.INFO):
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)
    current_logger = logging.getLogger(name)
    current_logger.setLevel(level)
    current_logger.addHandler(handler)
    return current_logger

# General logger to print errors in case environment cannot be determined.
logger = None
user_logger = None

def get_environment() -> str:
    # Check, which environment the script is running for; default to DEV.
    global environment
    global logger
    global user_logger
    
    available_env = ["DEV", "PROD", "OFFTOP"]
    printable_view_of_available_env = ", ".join(available_env)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--env", help="Environment, for which to run the script: " + printable_view_of_available_env)
    args = parser.parse_args()
    if args.env is not None:
        if args.env in available_env:
            environment = args.env
            logger = setup_logger('general', 'logs/ships_' + args.env +'.log')
            user_logger = setup_logger('user_logger', 'logs/users_' + args.env +'.log')
        else:
            logger = setup_logger('general', 'logs/ships.log')
            logger.error(f"Environment '{args.env}' not found in the list.")
    else:
        logger = setup_logger('general', 'logs/ships.log')
        logger.info("Environment was not provided, defaulting to DEV.")

    return environment or "DEV"

def get_bot_token_for_environment(environment):
    load_dotenv()
    bot_token = os.getenv('BOT_TOKEN_' + environment)
    if (bot_token is None):
        if (logger is not None):
            logger.error(f"Unable to find token for environment {environment}.")
    return bot_token

def get_users(environment):
    global users
    global user_logger
    csv_filename = "data/users_" + environment + ".csv"
    if(os.path.isfile(csv_filename)):
        with open(csv_filename, mode='r', newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                row['id'] = int(row['id'])
                users.append(row)
    else:
        if (user_logger is not None):
            user_logger.info(f"File {csv_filename} does not exist.")    
    if (user_logger is not None):
        user_logger.info(f"Loaded users: {users}'.")
    return users


def save_users(users):
    global environment
    csv_filename = "data/users_" + environment + ".csv"
    with open(csv_filename, mode='w', newline='') as csv_file:
        fieldnames = ['username', 'id']  # Define headers
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    
        writer.writeheader()  # Write the header row
        writer.writerows(users)  # Write all the rows

# /start:
#  - add user to list of tracked users (TBD: store this in DB!)
#  - print some kind of welcoming message
#  - TBD: print help message (store as a constant)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global users
    global user_logger
    global environment
    
    user = update.effective_user
    reply = 'Это дев-версия бота для разработки @AnonymousCaptainBot. Разработчик использует её для тестов. Стабильность не гарантирована.'
    if (environment == "PROD"):
        reply = '''
Это бот для анонимной ролевой игры. Как он устроен? Любое ваше игровое сообщение бот перешлёт всем остальным игрокам, 
котоыре подписаны на него. Пожалуйста, используйте бота-собрата, @AnonymousCaptainOfftopBot для любого неигрового оффтопа. 
Напишите /info чтобы увидеть список команд."
    '''
    if (environment == "OFFTOP"):
        reply = '''
Это бот для общения ролевиков, которые играют в @AnonymousCaptainBot. Как он устроен? Любое ваше сообщение бот перешлёт всем остальным игрокам, 
которые подписаны на него. Пожалуйста, общайтесь в оффтопе здесь, и используйте бота-собрата, @AnonymousCaptainBot для игр. 
Напишите /info чтобы увидеть список команд.
'''
    if (user is not None):
        user_ids = [u['id'] for u in users]
        if (user.id not in user_ids):
            users.append({'username': user.username, 'id': user.id})
            save_users(users)
            if (user_logger is not None):
                user_logger.info(f"User {user.username}, id {user.id} joined.")
            reply = rf"Добро пожаловать на борт, капитан {user.mention_html()}!" + reply
        else:
            reply = "Похоже, вы уже подписаны. Напомнить правила? " + reply
        if (update.message is not None):
            await update.message.reply_html(reply)

# /stop:
#  - remove user from list of tracked users (TBD: update DB!)
#  - print some kind of farewell message
#  - TBD: clear history so that they can't write to bot again
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global users
    global user_logger
    
    user = update.effective_user
    reply = rf"Вы отписаны от дальнейших сообщений. Чтобы снова включить обновления в этом чате, используйте команду /start."
    if (user is not None):
        users = [u for u in users if u['id'] != user.id]
        save_users(users)
        if (user_logger is not None):
            user_logger.info(f"User {user.username}, id {user.id} left.")
        
        if (update.message is not None):
            await update.message.reply_html(reply)


async def dispatch_to_all(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global users
    global logger
    
    user = update.effective_user
    if (user is not None and update.message is not None):
        messageText = update.message.text
        user_ids = [u['id'] for u in users]
        if (messageText is not None):
            if (user.id not in user_ids):
                reply = "Вы не подписаны на канал. Напишите команду /start, чтобы подписаться и снова отправлять сообщения."
                if (update.message is not None):
                    await update.message.reply_html(reply)
            else:
                if (logger is not None):
                    logger.info(
                        f"User id {user.id} sent message: {messageText} ")
                for user_id in user_ids:
                    try:
                        if (user_id != user.id):
                            await context.bot.send_message(chat_id=user_id, text=messageText)
                    except Exception as e:
                        logging.debug(f"Could not send message to {user_id}: {e}")

def main() -> None:
    # Starting the harbor...
    global environment
    environment = get_environment()
    bot_token = get_bot_token_for_environment(environment)
    get_users(environment)

    if (bot_token is not None):
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
