#Telegram bot that does 'stuff'

#libraries
from telegram.ext import MessageHandler, Filters, CommandHandler, Updater
import logging
import os
import re

#setting up and updater and dispatcher

updater = Updater(token = os.environ["TELEGRAM_BOT_TOKEN"], use_context = True)

dispatcher = updater.dispatcher

#setting up logging for easier debugging 

logging.basicConfig(format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s", level = logging.INFO)

#start function

def start(update, context):
    context.bot.send_message(chat_id = update.effective_chat.id, text = "Hello, I am property of the mathgod caliber.")

#calculator using regex

def calc(update, context):
	x = re.sub("[^0-9\+\-\*/\.\(\)]", "", "".join(context.args).replace("^", "**"))
	try:
		y = eval(x)
	except:
		y = "Invalid Input."
	update.effective_message.reply_text(y)


#command handlers

startHandler = CommandHandler("start", start)
calcHandler = CommandHandler("calc", calc)
dispatcher.add_handler(startHandler)   
dispatcher.add_handler(calcHandler) 

updater.start_polling()
