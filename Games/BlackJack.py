import random
from enum import Enum

class PlayerDecision(Enum):
	Hit = 1
	Stay = 2

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
	def populate(self):
		for suit in Card.suits:
			for rank in Card.ranks:
				card = Card(suit, rank)
				self.cards.append(card)
	def shuffle(self):
		random.shuffle(self.cards)
	def drawCard(self):
		if (len(self.cards) == 0):
			return False
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
		for x in range(numberOfAces):
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
	def __init__(self, ID, chips):
		self.ID = ID
		self.chips = chips
		self.currentBet = 0
		self.hand = Hand()
		self.roundResult = RoundResult.NoResult
	def placeBet(self, amount):
		if (amount <= self.chips):
			self.currentBet += amount
			self.chips -= amount
			return True
		return False
	def processResult(self):
		if (self.roundResult == RoundResult.Win):
			self.chips += self.currentBet * 2
		elif (self.roundResult == RoundResult.Push):
			self.chips += self.currentBet
		self.currentBet = 0

class BlackjackGame:
	def __init__(self):
		self.players = []
		self.currentPlayerIndex = 0
		self.dealerHand = Hand()
		self.deck = Deck()
		self.deck.populate()
	def startRound(self):
		self.deck.shuffle()
		for x in range(2):
			self.dealHands()
	def dealHands(self):
		for player in self.players:
			player.hand.addCard(self.deck.drawCard())
		self.dealerHand.addCard(self.deck.drawCard())
	def processDecision(self, decision):
		if (decision == PlayerDecision.Hit):
			player = self.players[self.currentPlayerIndex]
			player.hand.addCard(self.deck.drawCard())
			if (player.hand.isBust()):
				player.roundResult = RoundResult.Loss
				player.processResult()
				self.nextPlayer()
		elif (decision == PlayerDecision.Stay):
			self.nextPlayer()
	def nextPlayer(self):
		self.currentPlayerIndex += 1
		if (self.currentPlayerIndex == len(self.players)):
			self.endRound()
	def endRound(self):
		while (self.dealerHand.getValue() <= 16):
			self.dealerHand.addCard(self.deck.drawCard())
		dealerBust = self.dealerHand.isBust()
		for player in self.players:
			if (dealerBust):
				player.roundResult = RoundResult.Win
			else:
				if (player.hand.isBust()):
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
	def reset(self):
		for player in self.players:
			player.hand.clear()
			player.roundResult = RoundResult.NoResult
		self.dealerHand.clear()
		self.currentPlayerIndex = 0

game = BlackjackGame()
gamer = Player(1234, 50)
game.players.append(gamer)
while (True):
	try:
		chips = int(input(f"You have {gamer.chips} chips. How many chips do you wish to bet? "))
	except KeyboardInterrupt:
		print("no")
		quit()
	except:
		print("Invalid Input")
		continue
	x = gamer.placeBet(chips)
	if x:
		game.startRound()
		print("The dealer's first card is " + game.dealerHand.cards[0].toString())
		print("Your hand: " + gamer.hand.toString())
		while (True):
			choice = input("Do you want to hit or stay? ").lower()
			if (choice == "hit"):
				game.processDecision(PlayerDecision.Hit)
				print("Your hand: " + gamer.hand.toString())
				if (gamer.roundResult == RoundResult.Loss):
					print("Your hand is bust!")
					break
			elif (choice == "stay"):
				game.processDecision(PlayerDecision.Stay)
				break
			else:
				print("Invalid Input")
		print("Dealer's hand: " + game.dealerHand.toString())
		if (gamer.roundResult == RoundResult.Win):
			print("You Won!")
		elif (gamer.roundResult == RoundResult.Loss):
			print("You Lost!")
		elif (gamer.roundResult == RoundResult.Push):
			print("It's a Tie!")
		if (gamer.chips == 0):
			print("You're out of chips!")
			quit()
		print("You now have " + str(gamer.chips) + " chips")
		game.reset()
	else:
		print("You do not have those many chips to bet")