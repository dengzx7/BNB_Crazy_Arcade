import sys
import pygame
import time
from functions import *

import props
import plats
import bubbles
import heroes
import characters
import AIModel
import monsters

def play():

	mode = SingleMode()
	mode.solv()
	mode.end()

class SingleMode():
	screen = None

	def __init__(self):

		self.borders = [loadAndTransfer("images\\items\\border\\" + str(i) + ".png", setting.grid_scale, setting.grid_scale) for i in range(1, 5)]
		self.property_icon = [loadAndTransfer("images\\items\\property\\" + str(i) + ".png", setting.grid_scale*2, setting.grid_scale*2) for i in range(1, 4)]
		self.property = [loadAndTransfer("images\\items\\property\\" + str(i) + "_.png", setting.grid_scale, setting.grid_scale) for i in range(1, 4)]

		# 初始化地图
		self.plat = plats.Map()
		bubbles.Bubble.plat = self.plat
		characters.Character.plat = self.plat
		monsters.Monster.plat = self.plat
		monsters.Bleach.plat = self.plat


		self.chars = []
		name = heroes.randHero()
		color = heroes.randColor()
		# 初始化人物
		self.chars.append(characters.Character(name, color))
		# 初始化AI
		self.chars.append(AIModel.AI())

		monsters.Monster.chars = self.chars
		monsters.Bleach.chars = self.chars
		AIModel.AI.character = self.chars[0]

		# 初始化怪物
		self.monster = monsters.Monster()

		self.bleaches = []
		monsters.Bleach.bleaches = self.bleaches

		# 初始化道具记录榜
		self.propboard = props.PropBoard(self.screen)

		self.update_times = 0
		self.result = None	# 游戏结束的判断

	def solv(self):
		while self.result == None:
			self.check_events()
			self.update_screen()
			self.check_state()

	def check_state(self):
	#	pass
		if self.chars[0].state == 'died':
			self.result = "lose"
		else:
			for AI in self.chars:
				if isinstance(AI, AIModel.AI) and AI.state != 'died':
					return
			self.result = "win"

	def check_events(self):
		"""响应按键"""
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_RIGHT: self.chars[0].moving_right = True
				elif event.key == pygame.K_LEFT: self.chars[0].moving_left = True
				elif event.key == pygame.K_UP: self.chars[0].moving_up = True
				elif event.key == pygame.K_DOWN: self.chars[0].moving_down = True
				if event.key == pygame.K_SPACE:	self.chars[0].space = True
				if event.key == pygame.K_LCTRL: self.chars[0].ctrl = True

			elif event.type == pygame.KEYUP:
				if event.key == pygame.K_RIGHT: self.chars[0].moving_right = False
				elif event.key == pygame.K_LEFT: self.chars[0].moving_left = False
				elif event.key == pygame.K_UP: self.chars[0].moving_up = False
				elif event.key == pygame.K_DOWN: self.chars[0].moving_down = False
				if event.key == pygame.K_SPACE and not self.chars[0].blue_devil:	
					self.chars[0].space = False
				if event.key == pygame.K_LCTRL: self.chars[0].ctrl = False

	def update_screen(self):
		self.screen.fill(self.plat.color)

		self.update_times += 1	# 0630更新：跑马灯控制
		count = self.update_times // 80

		# 这个循环绘制 地图底层 和 边界
		for y in range(len(self.plat.g[0])):
			for x in range(len(self.plat.g)):
				item = self.plat.g[x][y]
				if isinstance(item, plats.T):
					self.screen.blit(self.borders[(count+y)%4], item.rect)
					count += 1
				elif type(item) != bool:
					self.screen.blit(item.image, item.rect)

		# 这个循环绘制 地图上层 和 人物
		for y in range(len(self.plat.g[0])):
			for x in range(len(self.plat.g)):
				item = self.plat.f1[x][y]
				if item != None:
					self.screen.blit(item.image, item.rect)
				if type(item) == plats.Box:
					item.pushing(self.chars)
					item.moving()					# 箱子移动
				if isinstance(item, bubbles.Bubble) :
					item.kick_bubble(self.chars)
					item.moving()

			for x in range(len(self.plat.g)):
				c = self.plat.c[x][y]
				for unit in c:
					unit.blit(self.screen)

				# 这个循环是为了 避免人物飞行时被下一行物体挡住
				c = self.plat.c[x-1][y-1]
				for unit in c:
					if isinstance(unit, characters.Character) and unit.ride_tag == 'f' and type(self.plat.f1[x][y]) != plats.Obstacle:
						unit.blit(self.screen)

		# 这个循环是为了 绘制bleach
		for y in range(len(self.plat.g[0])):
			for x in range(len(self.plat.g)):
				c = self.plat.c[x][y]
				for unit in c:
					if isinstance(unit, monsters.Bleach):
						unit.blit(self.screen)

		# 绘制人物属性
		for i in range(0, 3):
			self.screen.blit(self.property_icon[i], (680, 100 + i * 50))
		for i in range(0, self.chars[0].bubble_nums):				# 泡泡数量
			self.screen.blit(self.property[0], (740 + i * 40, 130))
		for i in range(0, self.chars[0].power):						# 泡泡威力
			self.screen.blit(self.property[1], (740 + i * 40, 180))
		for i in range(0, int((self.chars[0].speed - 1)/0.25)):		# 移动速度
			self.screen.blit(self.property[2], (740 + i * 40, 230))

		# 更新人物
		for char in self.chars:
			char.update()
			char.control()
			char.get_prop(self.propboard, type(char) == characters.Character)
			char.use_prop()

		self.monster.update()
		self.monster.kill()
		for bleach in self.bleaches:
			bleach.control()

		# 用于道具记录榜
		self.propboard.update_use(self.chars[0])
		self.propboard.show()

		pygame.display.update()

	def end(self):
#		self.screen.blit(functions.imgGray(self.screen), (0, 0))
		win_image_set = [pygame.image.load("images\\UI\\gameover\\win" +str(i)+".png").convert_alpha() for i in range(1, 13)]
		lose_image_set = [pygame.image.load("images\\UI\\gameover\\lose" +str(i)+".png").convert_alpha() for i in range(1, 21)]
		image = "images\\UI\\gameover\\" + self.result + ".png"
		image = pygame.image.load(image).convert_alpha()

		if self.result == "win":
			for i in range(0,12):
				roll_color = (255, 255, 255)
				self.screen.fill(roll_color)
				self.screen.blit(win_image_set[i], (450,100))
				time.sleep(0.07)
				pygame.display.flip()
		else:
			for i in range(0, 20):
				roll_color = (255, 255, 255)
				self.screen.fill(roll_color)
				self.screen.blit(lose_image_set[i], (450, 100))
				time.sleep(0.07)
				pygame.display.flip()
		self.screen.blit(image, (100, 50))
		pygame.display.flip()
		time.sleep(1)