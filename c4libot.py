#Telegram bot that does 'stuff'

#libraries
from Games.BlackJack import BlackjackGame
from Games import BlackJack as blackjack
from telegram.ext import MessageHandler, Filters, CommandHandler, Updater
from telegram import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup
import logging
import random
import requests
import threading
import os
import re
from enum import Enum

from telegram.ext.callbackqueryhandler import CallbackQueryHandler

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

blackjackMarkup = [[
	InlineKeyboardButton(text = "+50", callback_data="blackjack.place50"),
	InlineKeyboardButton(text = "+100", callback_data="blackjack.place100"),
	InlineKeyboardButton(text = "+250", callback_data="blackjack.place250"),
	InlineKeyboardButton(text = "+500", callback_data="blackjack.place500"),
	InlineKeyboardButton(text = "+All", callback_data="blackjack.placeAll"),
], [
	InlineKeyboardButton(text = "-All", callback_data="blackjack.removeAll"),
	InlineKeyboardButton(text = "End Game", callback_data="blackjack.end")
]]

def __init__(self, main, apiKey, enableTimer = False):
		self.main = main
		self.apiKey = apiKey
		self.enableTimer = enableTimer
		self.storedQueries = {}
		self.activeGames = {}
		self.blackjackDelay = 15
		self.blackjackStartingChips = 1000
		self.blackjackTimer = None
		self.skipBlackjackPlayerTimer = None
		self.results = {}
		self.lastResult = None
		self.start()

def playCommand(self, update, context):
	query = " ".join(context.args).strip().lower()
	if (query == "blackjack"):
		activeGame = self.activeGames["blackjack"].get(update.effective_chat.id)
	if (activeGame == blackjack.BlackJackGame):
		self.sendMessage(update.effective_chat, "Another game of Blackjack is already active in this chat. To stop the game, type /input stop.", update.message.message_id)
		return	
	sentMessage = self.sendMessage(update.effective_chat, f"<b>Blackjack</b>\n\nThe first round begins in {self.blackjackDelay} seconds.\nEach player starts with {self.blackjackStartingChips} chips.\nPlace your bets!", reply_markup = InlineKeyboardMarkup(inline_keyboard = self.blackjackMarkup))
	game = blackjack.BlackjackGame(sentMessage, update.effective_user.id)
	self.activeGames["blackjack"][update.effective_chat.id] = game
	self.blackjackTimer = threading.Timer(self.blackjackDelay, self.startBlackjackRound, [game])
	self.blackjackTimer.start()	


def callbackQueryHandler(self, update, context):
	if (not update.callback_query):
		return
	query = update.callback_query.data
	if (query.startswith("blackjack")):
		activeGame = self.activeGames["blackjack"].get(update.effective_chat.id)
		userID = update.effective_user.id
		if (query == "blackjack.end"):
			self.endBlackJackGame()
			self.answerCallbackQuery(update.callback_query, "You have ended the game.")
			return
		player = self.activeGames.players.get(userID)
		if (activeGame.roundStarted()):
			if (query not in ["blackjack.hit", "blackjack.stand"]):
					return
			if (not player or activeGame.currentPlayer.userID != userID):
				self.answerCallbackQuery(update.callback_query, "It's not your turn.")
				return
			self.skipBlackjackPlayerTimer.cancel()
			nextPlayerExists = False
			if (query == "blackjack.hit"):
				self.answerCallbackQuery(update.callback_query, "You decided to hit.")
				nextPlayerExists = activeGame.processDecision(blackjack.BlackJackGame.PlayerDecision.Hit)
				self.askBlackjackPlayer(activeGame, True, player, update.effective_message)
			elif (query == "blackjack.stand"):
				self.answerCallbackQuery(update.callback_query, "You decided to stand.")
				nextPlayerExists = activeGame.processDecision(blackjack.BlackJackGame.PlayerDecision.Stand)
				self.editMessageText(update.effective_message, f"{player.name}, your hand is valued at {player.hand.getValue()}.\n{player.hand.toString()}\n\nYou decided to stand.")
			if (nextPlayerExists):
				self.askBlackjackPlayer(activeGame)
			elif (nextPlayerExists == False):
				self.sendBlackjackResults(activeGame)
		else:
			chips = {"blackjack.place50": 50, "blackjack.place100": 100, "blackjack.place250": 250, "blackjack.place500": 500, "blackjack.placeAll": -1, "blackjack.removeAll": -2}.get(query, 0)		
			if (not chips):
					return
			if (not player):
				player = blackjack.BlackJackGame.Player(userID, update.effective_user.first_name, self.blackjackStartingChips)
				activeGame.players[userID] = player
			if (chips == -1):
					chips = player.chips
			elif (chips == -2):
				chips = -player.currentBet
			if (player.placeBet(chips)):
				if (chips < 0):
					self.answerCallbackQuery(update.callback_query, f"You removed {-chips} chips. You have {player.chips} chips left.")
				else:
					self.answerCallbackQuery(update.callback_query, f"You bet {chips} chips. You have {player.chips} chips left.")
				self.updateBlackjackBetMessage(activeGame)
			else:
				if (player.currentBet <= 0 and query == "blackjack.removeAll"):
					self.answerCallbackQuery(update.callback_query, "You haven't placed any bet.")
				else:
					if (player.chips == 0):
						self.answerCallbackQuery(update.callback_query, "You don't have any chips left.")
					else:
						self.answerCallbackQuery(update.callback_query, f"You only have {player.chips} chips left.")		

def endBlackJackGame(self, game, noBets = False):
	if (not game.roundStarted):
		self.updateBlackjackBetMessage(game, True)
	noBets = "No one placed any bets. " if noBets else ""	
	if (len(game.players) > 0):
		playersText = "\n\nFinal Chip Balances: "
		playersSorted = dict(sorted(game.players.items(), key = lambda x: (x[1].chips + x[1].currentBet), reverse = True))
		for userID, player in playersSorted.items():
			playersText += f"\n{player.name} - {player.chips + player.currentBet}"
	else:
		playersText = ""
	self.sendMessage(game.message.chat, f"<b>Blackjack</b>\n\n{noBets}The game has ended." + playersText)
	self.blackjackTimer.cancel()
	self.skipBlackjackPlayerTimer.cancel()
	del self.activeGames["blackjack"][game.message.chat.id]

def sendBlackJackResult(self, game):
	isBust = ""
	if (game.dealerHand.isBust()):
		isBust = "\nIt's a bust!"
	results = ""
	for userID, player in game.players.items():
		results += f"\n{player.name} [{player.hand.getValue()}] "
		if (player.roundResult == blackjack.BlackJackGame.RoundResult.Win):
			results += f"has won {player.currentBet} chips and now has {player.chips + (player.currentBet * 2)} chips."
		elif (player.roundResult == blackjack.BlackJackGame.RoundResult.Loss):
			results += f"has lost {player.currentBet} chips and has {player.chips} chips left."
		elif (player.roundResult == blackjack.BlackJackGame.RoundResult.Push):
			results += f"has tied with the dealer and has {player.chips} chips."
		elif (player.roundResult == blackjack.BlackJackGame.RoundResult.NoResult):
			results += f"did not participate and has {player.chips} chips."
	self.sendMessage(game.message.chat, f"The dealer's hand is valued at {game.dealerHand.getValue()}.\n{game.dealerHand.toString()}{isBust}\n{results}\n\nThe round has ended.")
	game.processResult()
	game.message = self.sendMessage(game.message.chat, f"The next round begins {self.blackjackDelay} seconds after the first bet.\nPlace your bets!", reply_markup = InlineKeyboardMarkup(inline_keyboard = self.blackjackMarkup))

def startBlackjackRound(self, game):
	self.blackjackTimer = None
	if (sum(player.currentBet for userID, player in game.players.items()) == 0):
		self.endBlackjackGame(game, True)
		return
	self.updateBlackjackBetMessage(game, True)
	game.startRound()
	self.sendMessage(game.message.chat, f"The round has begun. Everyone has been dealt two cards.\nThe dealer's first card is {game.dealerHand.cards[0].toString()}.")
	self.askBlackjackPlayer(game)


def askBlackjackPlayer(self, game, edit = False, player = None, message = None):
	if (not player):
		player = game.currentPlayer
	if (not message):
		message = game.message
	if (edit):
		methodToCall = lambda *args, **kwargs: self.editMessageText(message, *args, **kwargs)
	else:
		methodToCall = lambda *args, **kwargs: self.sendMessage(message.chat, *args, **kwargs)
	if (player.hand.isBust()):
		methodToCall(f"{player.name}, your hand is valued at {player.hand.getValue()}.\n{player.hand.toString()}\nIt's a bust!")
	else:
		sentMessage = methodToCall(f"{player.name}, your hand is valued at {player.hand.getValue()}.\n{player.hand.toString()}\n\nDo you want to hit or stand?", reply_markup = InlineKeyboardMarkup(inline_keyboard = [[
			InlineKeyboardButton(text = "Hit", callback_data = "blackjack.hit"),
			InlineKeyboardButton(text = "Stand", callback_data = "blackjack.stand")
		]]))
		self.skipBlackjackPlayerTimer = threading.Timer(20, self.skipBlackjackPlayer, [game, sentMessage])
		self.skipBlackjackPlayerTimer.start()

def skipBlackjackPlayer(self, game, message):
	player = game.currentPlayer
	nextPlayerExists = game.processDecision(blackjack.BlackJackGame.PlayerDecision.Stand)
	self.editMessageText(message, f"{player.name}, your hand is valued at {player.hand.getValue()}.\n{player.hand.toString()}\n\nYou decided to stand (20 second timeout).")
	if (nextPlayerExists):
		self.askBlackjackPlayer(game)
	elif (nextPlayerExists == False):
		self.sendBlackjackResults(game)

def updateBlackjackBetMessage(self, game, roundStarting = False):
	playersText = ""
	for userID, player in game.players.items():
		if (player.currentBet > 0):
			playersText += f"\n{player.name} has bet {player.currentBet} chips and has {player.chips} chips left."
	secondsText = f"in {self.blackjackDelay} seconds"
	replyMarkup = self.blackjackMarkup
	if (game.started):
		if (not playersText):
			secondsText = f"{self.blackjackDelay} seconds after the first bet"
		initialText = f"The next round begins {secondsText}.\nPlace your bets!\n"
	else:
		initialText = f"<b>Blackjack</b>\n\nThe first round begins {secondsText}.\nEach player starts with {self.blackjackStartingChips} chips.\nPlace your bets!\n"
	if (roundStarting):
		replyMarkup = None
		if (game.started):
			initialText = "The next round is about to begin.\n"
		else:
			initialText = "<b>Blackjack</b>\n\nThe first round is about to begin.\n"
	else:
		replyMarkup = InlineKeyboardMarkup(inline_keyboard = replyMarkup)
		if (self.blackjackTimer == None and playersText):
			self.blackjackTimer = threading.Timer(self.blackjackDelay, self.startBlackjackRound, [game])
			self.blackjackTimer.start()
	game.message = self.editMessageText(game.message, initialText + playersText, reply_markup = replyMarkup)


#command handlers

startHandler = CommandHandler("start", start)
calcHandler = CommandHandler("calc", calc)
cattoHandler = CommandHandler("catto", catto)
stopHandler = CommandHandler("stopcat", stop)
playHandler = CommandHandler("play", playCommand)
callbackqueryHandler = CallbackQueryHandler(playHandler)
dispatcher.add_handler(startHandler)   
dispatcher.add_handler(calcHandler) 
dispatcher.add_handler(cattoHandler)    
dispatcher.add_handler(stopHandler)
dispatcher.add_handler(playHandler)
dispatcher.add_handler(callbackqueryHandler)

updater.start_polling()
