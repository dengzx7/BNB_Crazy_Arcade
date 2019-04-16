import sys

import pygame

from settings import Settings

import time


def run_game():

	#初始化游戏并创建一个屏幕对象
	pygame.init()
	ai_settings = Settings()
	screen = pygame.display.set_mode(
		(ai_settings.screen_width, ai_settings.screen_height))
	pygame.display.set_caption("Alien Invasion")
#	surface = pygame.Surface((50, 55), depth=32)
#	surface.set_alpha(0)
	image1 = pygame.image.load("images\\hero\\huasha\\red1.png")
	rect = image1.get_rect()
	rect.centerx += 20
	rect.centery += 20
	
	invertImg(image1)

	#开始游戏的主循环
	while True:

		#监视键盘和鼠标事件
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()

		#每次循环时都重绘屏幕
		screen.fill(ai_settings.bg_color)
		screen.blit(image1, rect)

		
		#让最近绘制的屏幕可见
		pygame.display.flip()

run_game()