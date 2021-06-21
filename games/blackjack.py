import random
from enum import Enum

class PlayerDecision(Enum):
	Hit = 1
	Stand = 2

class RoundResult(Enum):
	NoResult = 1
	Win = 2
	Loss = 3
	Push = 4


class Card:

	suits = ["♣", "♦", "♥", "♠"]
	ranks = range(1, 14)
	rankText = ["Ace", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Jack", "Queen", "King"]

	def __init__(self, suit, rank):
		self.suit = suit
		self.rank = rank

	def toString(self):
		return f"({self.rankText[self.rank - 1]} of {self.suit})"

class Deck:

	def __init__(self):
		self.cards = []
	def populate(self, decks):
		self.cards += [Card(suit, rank) for x in range(decks) for suit in Card.suits for rank in Card.ranks]
	def shuffle(self):
		random.shuffle(self.cards)
	def drawCard(self):
		if (len(self.cards) == 0):
			self.populate(4)
			self.shuffle()
		return self.cards.pop()

class Hand:

	def __init__(self):
		self.cards = []

	def addCard(self, card):
		self.cards.append(card)

	def clear(self):
		self.cards.clear()

	def getValue(self):
		numberOfAces = 0
		handValue = 0
		for card in self.cards:
			valueToAdd = min(card.rank, 10)
			if (card.rank == 1):
				numberOfAces += 1
				valueToAdd = 11
			handValue += valueToAdd
		for _ in range(numberOfAces):
			if (handValue > 21):
				handValue -= 10
		return handValue

	def isBust(self):
		return (self.getValue() > 21)

	def toString(self):
		handStrings = []
		for card in self.cards:
			handStrings.append(card.toString())
		return (", ".join(handStrings) + f", [{self.getValue()}]")

class Player:

	def __init__(self, name, userID, chips):
		self.name = name
		self.userID = userID
		self.chips = chips
		self.currentBet = 0
		self.hand = Hand()
		self.roundResult = RoundResult.NoResult

	def placeBet(self, amount):
		if (amount >= -self.currentBet and amount <= self.chips and amount != 0):
			self.currentBet += amount
			self.chips -= amount
			return True
		return False

	def processResult(self):
		self.hand.clear()
		if (self.roundResult == RoundResult.Win):
			self.chips += self.currentBet * 2
		elif (self.roundResult == RoundResult.Push):
			self.chips += self.currentBet
		self.currentBet = 0
		self.roundResult = RoundResult.NoResult

class Game:

	def __init__(self, message, starterUserID):
		self.message = message
		self.starterUserID = starterUserID
		self.started = False
		self.roundStarted = False
		self.players = {}
		self.currentPlayer = None
		self.currentPlayerIndex = -1
		self.dealerHand = Hand()
		self.deck = Deck()

	def startRound(self):
		self.nextPlayer()
		self.started = True
		self.roundStarted = True
		self.deck.shuffle()
		for _ in range(2):
			self.dealHands()

	def dealHands(self):
		for userID, player in self.players.items():
			if (player.currentBet > 0):
				player.hand.addCard(self.deck.drawCard())
		self.dealerHand.addCard(self.deck.drawCard())

	def processDecision(self, decision):
		if (decision == PlayerDecision.Hit):
			player = self.players[self.currentPlayerIndex]
			player.hand.addCard(self.deck.drawCard())
			if (player.hand.isBust()):
				self.currentPlayer.roundResult = RoundResult.Loss
				return self.nextPlayer()
		elif (decision == PlayerDecision.Stand):
			return self.nextPlayer()

	def nextPlayer(self):
		self.currentPlayerIndex += 1
		if (self.currentPlayerIndex == len(self.players)):
			self.endRound()
			return False
		self.currentPlayer = self.players[list(self.players.keys())[self.currentPlayerIndex]]
		if (self.currentPlayer.currentBet == 0):
			return self.nextPlayer()
		return True

	def endRound(self):
		while (self.dealerHand.getValue() <= 16):
			self.dealerHand.addCard(self.deck.drawCard())
		dealerBust = self.dealerHand.isBust()
		for userID, player in self.players.items():
			if (dealerBust):
				player.roundResult = RoundResult.Win
			else:
				if (player.hand.isBust() or player.currentBet <= 0):
					continue
				playerHandValue = player.hand.getValue()
				dealerHandValue = self.dealerHand.getValue()
				if (playerHandValue < dealerHandValue):
					player.roundResult = RoundResult.Loss
				elif (playerHandValue > dealerHandValue):
					player.roundResult = RoundResult.Win
				else:
					player.roundResult = RoundResult.Push
			player.processResult()

	def processResult(self):
		for userID, player in self.players.items():
			player.processResult()
		self.dealerHand.clear()
		self.currentPlayerIndex = -1
		self.roundStarted = False
