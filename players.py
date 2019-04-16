import pygame
import heroes
from functions import *

class Player(object):
	def __init__(self, clientNO, hero, color, pos):
		self.name = "client" + str(clientNO)
		self.hero = hero
		self.color = color
		self.pos = pos				# 玩家在房间的位置
		self.image = loadAndTransferHeroImage("images\\hero\\" + self.hero + "\\pd0.png", self.color)
		font = pygame.font.SysFont(None, 48)
		self.name_image = font.render(self.name, True, (25, 25, 75)).convert_alpha()

	def blit(self, screen):
		rect = self.image.get_rect()
		rect.centerx = 150 + 150*(self.pos%4)
		rect.centery = 150 + 150*(self.pos//4)
		screen.blit(self.image, rect)

		name_rect = self.name_image.get_rect()
		name_rect.centerx, name_rect.centery = rect.centerx, rect.centery - 60

		screen.blit(self.name_image, name_rect)
		
	def changeColor(self, color):
		self.color = color
		self.image = loadAndTransferHeroImage("images\\hero\\" + self.hero + "\\pd0.png", self.color)
