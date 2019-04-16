import sys
import pygame

from functions import *
from settings import Settings
from image_roll import image_rolling
import button
import singleMode
import pushBoxMode
import netMode


class BNBGame():
	def __init__(self):
		# 初始化
		pygame.init()
		self.bnb_settings = Settings()
		self.screen = pygame.display.set_mode(
			(self.bnb_settings.screen_width, self.bnb_settings.screen_height))
		singleMode.SingleMode.screen = self.screen
		netMode.NetMode.screen = self.screen
		pushBoxMode.PushBoxMode.screen = self.screen


		pygame.display.set_caption("BNB")

		#初始化图片文件
		self.background = pygame.image.load('images\\surface.png').convert_alpha()
		self.title = pygame.image.load('images\\title.png').convert_alpha()
		self.logo = pygame.image.load('images\\logo.png').convert_alpha()

	def run_game(self, clientNO=None):

		mybuttons = button.BottonMain()

		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()
				if event.type == pygame.MOUSEBUTTONUP:
					if mybuttons.buttons[0].isOver():	# 单人模式
						singleMode.play()
						continue
					elif mybuttons.buttons[1].isOver():	# 联机模式
						netMode.play(clientNO)
						continue
					elif mybuttons.buttons[2].isOver():	# 退出游戏
						pushBoxMode.play()
						continue
					elif mybuttons.buttons[3].isOver(): #制作名单
						image_rolling(self.screen)
						continue
			self.screen.blit(self.background, (0, 0))
			self.screen.blit(self.title, (300, 0))
			self.screen.blit(self.logo, (700, 20))
			# screen.blit(background, (0,0))
			# screen.blit(logo, ((SCREEN_SIZE[0]-logo.get_width())/2,100))
			mybuttons.render(self.screen)
			pygame.display.update()

if __name__ == '__main__':
	bnb = BNBGame()
	bnb.run_game()