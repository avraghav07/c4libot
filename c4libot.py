#Telegram bot that does 'stuff'

#libraries
from telegram.ext import MessageHandler, Filters, CommandHandler, Updater
import logging
import os

#setting up and updater and dispatcher

updater = Updater(token = os.environ["TELEGRAM_BOT_TOKEN"], use_context = True)

dispatcher = updater.dispatcher

#setting up logging for easier debugging 

logging.basicConfig(format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s", level = logging.INFO)

#start function

def start(update, context):
    context.bot.send_message(chat_id = update.effective_chat.id, text = "Hello, I am property of the mathgod caliber.")



startHandler = CommandHandler("start", start)
dispatcher.add_handler(startHandler)    

updater.start_polling()
