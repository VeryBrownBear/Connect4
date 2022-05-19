import pygame
from collections import defaultdict

bestMove = None
screen = pygame.display.set_mode((700, 600))
boardIMG = pygame.image.load("board.png")
font = pygame.font.SysFont("comicsansms", 50)
transpositionTable = defaultdict(lambda: None)
