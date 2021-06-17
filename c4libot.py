#Telegram bot that does 'stuff'

#libraries
from telegram.ext import MessageHandler, Filters, CommandHandler, Updater
import logging
import random
import requests
import threading
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

#cat spam function that sends a cat pic (taken from a free api using request.get) every 5 seconds using a global timer for every chat

timers = {}

def catto(update, context):
	global timers
	data = requests.get("https://api.thecatapi.com/v1/images/search").json()
	update.effective_chat.send_photo(data[0]["url"])
	if update.effective_chat.id in timers and timers[update.effective_chat.id].is_alive():
		timers[update.effective_chat.id].cancel()
	timers[update.effective_chat.id] = threading.Timer(2.0, catto, [update, context])
	timers[update.effective_chat.id].start()

def stop(update, context):
	global timers
	if update.effective_chat.id in timers and timers[update.effective_chat.id].is_alive():
		timers[update.effective_chat.id].cancel()
		del timers[update.effective_chat.id]        


#command handlers

startHandler = CommandHandler("start", start)
calcHandler = CommandHandler("calc", calc)
cattoHandler = CommandHandler("catto", catto)
stopHandler = CommandHandler("stopcat", stop)
dispatcher.add_handler(startHandler)   
dispatcher.add_handler(calcHandler) 
dispatcher.add_handler(cattoHandler)    
dispatcher.add_handler(stopHandler)

updater.start_polling()
