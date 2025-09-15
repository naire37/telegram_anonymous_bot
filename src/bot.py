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


# Global variables. Global variables are evil, but quite effecient.

environment = "DEV"
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
logger = None
user_logger = None 
users = [] # stored as array of dictionaries in format {username: "lee", id: "123"}
# This is ugly but this message ids must be tracked accross bot for edit, delete and expire functionality
messages = [] # stored as array of dictionaries in format {sender_id, sender_message_id, recepient_id, recepient_message_id, timestamp}

def setup_logger(name, log_file, level=logging.INFO):
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)
    current_logger = logging.getLogger(name)
    current_logger.setLevel(level)
    current_logger.addHandler(handler)
    return current_logger

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

def get_last_deleted_message_id(environment):
    global logger

    deleted_message_file = "data/last_deleted_message_" + environment + ".txt"
    if(os.path.isfile(deleted_message_file)):
        with open(deleted_message_file, 'r') as f:
            number_str = f.read()
            number = int(number_str)
            return number
    else:
        return 1

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
Это бот для анонимной ролевой игры. Он анонимно пересылает посты всем остальным игрокам. 
Для общения в оффтопе: @AnonymousCaptainOfftopBot. 
Напишите /info чтобы увидеть список команд.
    '''
    if (environment == "OFFTOP"):
        reply = '''
Это бот для общения ролевиков. Он анонимно пересылает посты всем остальным игрокам. 
Для игры: @AnonymousCaptainBot. 
Напишите /info чтобы увидеть список команд.
'''
    if (user is not None):
        user_ids = [u['id'] for u in users]
        if (user.id not in user_ids):
            users.append({'username': user.username, 'id': user.id})
            save_users(users)
            if (user_logger is not None):
                user_logger.info(f"User {user.username}, id {user.id} joined.")
            reply = rf"Добро пожаловать, {user.mention_html()}! " + reply
        else:
            reply = "Вы уже подписаны. Нажмите /info чтобы увидеть список команд."
        if (update.message is not None):
            await update.message.reply_html(reply)

# /stop:
#  - remove user from list of tracked users (TBD: update DB!)
#  - print some kind of farewell message
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

# /info:
#  - prints list of commands
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global environment
    reply = ''
    if (environment == "PROD" or environment == "DEV"):
        reply = "Ролевой канал. "
    if (environment == "OFFTOP"):
        reply = "Неролевой канал. "

    reply = reply + rf''' Доступные команды:
/info или /help - показать это сообщение
/start — подписаться
/stop - отписаться
/stats - информация о канале

Работает:
- редактирование своих сообщений (будьте бдительны: в боте не будет отметки о том, что сообщение было отредактированно)

Удаление сообщений:
/delete - отвечая на своё сообщение этой командой, вы можете удалить это сообщение у всех. Внимание! Если вы просто удалите сообщение у себя, оно останется у всех остальных пользователей.

Пока не работают:
- ответить на сообщение
- личные сообщения
- таймер антиспама
- таймер сгорания сообщений
- опция "пожаловаться"
- вставка медиа-контента

А что будет, если:
- удалить чужое сообщение: оно удалится только у вас.
- удалить своё сообщениеL оно удалится только у вас.

'''
    if (update.message is not None):
        await update.message.reply_html(reply)

# /stats:
#  - prints number of users
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    reply = f"Текущее количество пользователей: {len(users)}."
    if (update.message is not None):
        await update.message.reply_html(reply)

# handles new messages and edits.
async def add_or_edit_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global users
    global logger
    
    user = update.effective_user
    if (user is not None and update.message is not None):
        messageText = update.message.text
        originalMessageId = update.message.id
        messageTimestamp = update.message.date
        user_ids = [u['id'] for u in users]
        if (messageText is not None):
            if (user.id not in user_ids):
                reply = "Вы не подписаны на канал. Напишите команду /start, чтобы подписаться и снова отправлять сообщения."
                if (update.message is not None):
                    await update.message.reply_html(reply)
            else:
                track_message(user.id, originalMessageId, None, None, messageTimestamp)
                for user_id in user_ids:
                    try:
                        if (user_id != user.id):
                            forwarded_message = await context.bot.send_message(chat_id=user_id, text=messageText)
                            track_message(user.id, originalMessageId, user_id, forwarded_message.id, messageTimestamp)
                    except Exception as e:
                        if (logger is not None):
                            logger.info(f"Could not send message to {user_id}: {e}")
    if (update.edited_message is not None):
        await handle_update(context, update.edited_message)

async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global messages
    global logger
    
    message = update.message
    if (message is not None):
        message_to_delete = message.reply_to_message
        if (message_to_delete is not None and message.from_user is not None and message_to_delete.from_user is not None):
            if (message.from_user.id != message_to_delete.from_user.id):
                await message.reply_html("Вы пытаетесь удалить чужое сообщение. Вы можете удалить его локально у себя, используя функционал Телеграм.")
            else:
                # iterate over copy of messages because deleting will mess up with iterator otherwise.
                for m in messages[:]:
                    if message.from_user.id  == m['s_id'] and message_to_delete.message_id == m['s_mes_id']:
                        recepient_id = m['r_id']
                        recepient_message_id = m['r_mes_id']
                        if (recepient_id is not None and recepient_message_id is not None):
                            await context.bot.delete_message(chat_id=recepient_id, message_id=recepient_message_id)
                        #Else this message is a copy user sent to themselves
                        else:
                            await context.bot.delete_message(chat_id=message.from_user.id, message_id=message_to_delete.id)
                        messages.remove(m)
        # Finally, delete the "/delete" message itself.
        if (message.from_user is not None):
            await context.bot.delete_message(chat_id=message.from_user.id, message_id=message.id)


# Helper function to track all messages.
def track_message(sender_id, sender_message_id, recepient_id, recepient_message_id, timestamp):
    global logger
    global messages
    if (logger is not None):
        logger.info(
           f"Sender {sender_id} sent message {sender_message_id}, forwarded to recepient {recepient_id} as message {recepient_message_id} at {timestamp}.")
        messages.append({'s_id': sender_id, 's_mes_id': sender_message_id, 'r_id':recepient_id, 'r_mes_id': recepient_message_id, 'created': timestamp})
    return


# Helper function to find receiver message id by sender, original message id and receiver. Returns none if corresponding id is not found.
def get_recepient_message_id(sender_id, sender_message_id, recepient_id):
    global messages

    for message in messages:
        if sender_id == message['s_id'] and sender_message_id == message['s_mes_id'] and recepient_id == message['r_id']:
            return message['r_mes_id']
    return None  # if corresponding message id is not found

    
async def handle_update(context, message):
    global users
    global logger
    global messages

    new_message = message.text
    sender_id = message.from_user.id
    original_message_id = message.message_id

    if (logger is not None):
        logger.info(f"Sender id {sender_id}, original message id {original_message_id}, new text is {new_message}")

    
    user_ids = [u['id'] for u in users]
    if (sender_id not in user_ids):
        reply="Вы не подписаны на канал. Напишите команду /start, чтобы подписаться и снова отправлять сообщения."
        if (message is not None):
            await message.reply_html(reply)

    else:
        for recepient_id in user_ids:
            try:
                if (recepient_id != sender_id):
                    # Find the respective message to edit and edit it.
                    message_id_for_recepient = get_recepient_message_id(sender_id, original_message_id, recepient_id)
                    if (message_id_for_recepient is not None):
                        await context.bot.edit_message_text(chat_id=recepient_id, message_id=message_id_for_recepient, text=new_message)
            except Exception as e:
                if (logger is not None):
                    logger.info(f"Could not edit a message: {e}")


# For deleting a message bot must delete all isntances of that message accross all chats. 
#     dispatcher.add_handler(MessageHandler(Filters.update.edited_message, edited_message_handler))


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
        application.add_handler(CommandHandler("info", info))
        application.add_handler(CommandHandler("help", info))
        application.add_handler(CommandHandler("stats", stats))     
        application.add_handler(CommandHandler("delete", delete))     
        application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, add_or_edit_message))       


        # Run the bot until the user presses Ctrl-C
        application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
