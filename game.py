import pygame
pygame.init()
import pygame.font
pygame.font.init()
import numpy as np
import config
import copy
import time

class Player():
	def __init__(self, name):
		self.name = name

	def color(self):
		if self.name == 1:
			return (255, 0, 0)
		if self.name == 2:
			return (255, 255, 0)
			
class Game():
	def __init__(self, gameBoard = None):
		self.players = [Player(1), Player(2)]
		self.player = self.players[0]
		self.rows = 6
		self.cols = 7
		if gameBoard != None: self.gameBoard = gameBoard
		else: self.gameBoard = np.array([[0 for i in range(self.cols)] for j in range(self.rows)])
		
		self.height = 600
		self.size = 80
		self.offset = 10
		self.pieceOffset = 20
		self.radius = self.size // 2
    
		self.gameOver = False
		self.clicked = False
		
		self.aiTurn = False
		self.availableMoves = set()
		self.movesMade = 0

	# Iterates through each column in the board to see if there are any 0's in them
	# If there is a 0, add it to the list of available moves
	def generateAvailableMoves(self):
		self.availableMoves = set(i for i in range(7) if (self.gameBoard[:, i].min() == 0))

	# Finds the index of the first instance of a 0 in a column
	# Marks the position with the current player's mark
	def makeMove(self, column):
		row = np.argmin(self.gameBoard[:, column] != 0)
		self.gameBoard[row, column] = self.player.name
		self.movesMade += 1
		return row
	
	# Changes the current player's turn according to the current player
	def changePlayer(self):
		if self.player == self.players[0]:
			self.player = self.players[1]
		else:
			self.player = self.players[0]

	# Checks for 4 in a row in all directions
	def checkWinner(self, player):
		# Shortest amount of moves to win a game is 7 moves
		if self.movesMade < 7: return False
		board = self.gameBoard
		# Check vertical win
		for col in range(self.cols):
			for row in range(self.rows - 3):
				if board[row][col] == player.name and board[row + 1][col] == player.name and board[row + 2][col] == player.name and board[row + 3][col] == player.name:
					self.gameOver = True							
					return True
		# Check horizontal win
		for col in range(self.cols - 3):
			for row in range(self.rows):
				if board[row][col] == player.name and board[row][col + 1] == player.name and board[row][col + 2] == player.name and board[row][col + 3] == player.name:
					self.gameOver = True
					return True
		# Checking diagonal wins
		for col in range(self.cols - 3):
			for row in range(self.rows - 3):
				if board[row][col] == player.name and board[row + 1][col + 1] == player.name and board[row + 2][col + 2] == player.name and board[row + 3][col + 3] == player.name:
					self.gameOver = True
					return True
		for col in range(self.cols - 3):
			for row in range(3, self.rows):
				if board[row][col] == player.name and board[row - 1][col + 1] == player.name and board[row - 2][col + 2] == player.name and board[row - 3][col + 3] == player.name:
					self.gameOver = True
					return True
		return False

	# Initialize display
	def startBoard(self):
		config.screen.fill((255, 255, 255))
		self.drawBoard()
	
	# Creates the board if there has not been a move made
	# If there has been a move made, then make marker at given position
	def drawBoard(self, player = None, row = None, column = None):
		if player != None:
			pygame.draw.circle(config.screen, player.color(), (self.offset + self.radius + self.pieceOffset * column + self.size * column, self.height - self.size * row - self.pieceOffset * row - 50), self.radius)
			pygame.display.flip()
		else:
			config.screen.blit(config.boardIMG, (0, 0))
			pygame.display.flip()

	# Displays the win text screen
	def drawWinner(self):
		text = f"Player {self.player.name} won!"
		text = config.font.render(text, True, (0, 255, 0))
		config.screen.blit(text, (200, 0))
		pygame.display.flip()

	# Scoring a possible 4 in a row
	def scoreLine(self, line):
		score = 0
		opponent = 1
		if self.player.name == 1: opponent = 2
		if line.count(self.player.name) == 4: score += 100
		elif line.count(self.player.name) == 3 and line.count(0) == 1: score += 5
		elif line.count(self.player.name) == 2 and line.count(0) == 2: score += 2
		elif line.count(opponent) == 3 and line.count(0) == 1: score -= 4
		return score
	
	def scorePosition(self):
		score = 0
		centercol = [int(i) for i in list(self.gameBoard[:, self.cols // 2])]
		centercount = centercol.count(self.player.name)
		score += centercount * 5
		for row in range(self.rows):
			rowItems = [int(i) for i in list(self.gameBoard[row, :])]
			for col in range(self.cols - 3):
				line = rowItems[col: col + 4]
				score += self.scoreLine(line)
		for col in range(self.cols):
			colItems = [int(i) for i in list(self.gameBoard[:, col])]
			for row in range(self.rows - 3):
				line = colItems[row: row + 4]
				score += self.scoreLine(line)
		for row in range(self.rows - 3):
			for col in range(self.cols - 3):
				line = [self.gameBoard[row + i][col + i] for i in range(4)]
				score += self.scoreLine(line)
		for row in range(self.rows - 3):
			for col in range(self.cols - 3):
				line = [self.gameBoard[row + 3 - i][col + i] for i in range(4)]
				score += self.scoreLine(line)
		return score

	# Generates a new game state
	def makeNewGame(self, move):
		newGame = copy.deepcopy(self)
		newGame.makeMove(move)
		newGame.generateAvailableMoves()
		newGame.changePlayer()
		return newGame

	def minimax(self, depth, a, b):
		if self.checkWinner(self.players[1]): return 1000
		if self.checkWinner(self.players[0]): return -1000
		if depth == 0 or not self.availableMoves:
			return self.scorePosition()
		moves = []
		for move in self.availableMoves:
			newGame = self.makeNewGame(move)
			score = newGame.minimax(depth - 1, a, b)
			scoredMove = (move,  score)
			if self.player.name == 2:
				moves.append(scoredMove)
				if scoredMove[1] > a: 
					a = scoredMove[1]
			if self.player.name == 1:
				if scoredMove[1] < b: 
					b = scoredMove[1]
			if b < a: break
		if self.player.name == 1: return b
		config.bestMove = max(moves, key = lambda i: i[1])
		config.transpositionTable[self.gameBoard.tostring()] = config.bestMove
		return a

	# Game loop
	def play(self, ai):
		self.startBoard()
		while self.gameOver == False:
			if self.aiTurn:
				self.generateAvailableMoves()
				startTime = time.time()
				self.minimax(4, -10000, 10000)
				endTime = time.time()
				print(f"Calculated the best move in column {config.bestMove[0]} with score {config.bestMove[1]}, in {round(endTime - startTime, 5)} seconds")
				row = self.makeMove(config.bestMove[0])
				self.drawBoard(self.player, row, config.bestMove[0])
				if self.checkWinner(self.player):
					self.gameOver = True
					self.drawWinner()
					print(self.gameBoard)
					pygame.time.wait(5000)
				self.changePlayer()
				self.aiTurn = False
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.gameOver = True
				if event.type == pygame.MOUSEBUTTONDOWN and self.clicked == False and self.aiTurn == False:
					self.clicked = True
				if event.type == pygame.MOUSEBUTTONUP and self.clicked == True and self.aiTurn == False:
					self.clicked = False
					col = pygame.mouse.get_pos()[0] // 100
					self.generateAvailableMoves()
					if col in self.availableMoves:
						row = self.makeMove(col)
						self.drawBoard(self.player, row, col)
						if self.checkWinner(self.player):
							self.gameOver = True
							self.drawWinner()
							print(self.gameBoard)
							pygame.time.wait(5000)
						self.changePlayer()
						if ai:
							self.aiTurn = True
			pygame.display.update()
		pygame.quit