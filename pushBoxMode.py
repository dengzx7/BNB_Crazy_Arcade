import sys
import pygame

from functions import *
import button
import bubbles
import characters
import props
import plats
import BNB
import _thread
import time

def play():
	mode = PushBoxMode()
	mode.solv()

class PushBoxMode():
	screen = None

	def InitMap(self, map_id):
		# 初始化地图
		self.plat = plats.SoMap(map_id)
		
		bubbles.Bubble.plat = self.plat
		characters.Character.plat = self.plat

		# 初始化人物
		self.character = characters.Character()

		# 初始化道具记录榜
		self.propboard = props.PropBoard(self.screen)

		self.result = None
	
	def solv(self):

		self.menu()

		gmbuttons = button.ButtonGame(setting)
		gmbuttons.render(self.screen)

		while self.result == None:
			self.check_events(gmbuttons)
			self.update_screen(gmbuttons)

	def menu(self):
		sobuttons = button.ButtonSokoban(setting)	# 推箱子地图

		#self.screen.fill((0, 0, 0))
		#绘制背景 新的添加
		#初始化背景
		self.sur_image = pygame.image.load('images\\UI\\push_box\\surface.png').convert_alpha()
		self.add_image = pygame.image.load('images\\UI\\push_box\\add1.png').convert_alpha()
		self.screen.blit(self.sur_image, (0, 0))
		self.screen.blit(self.add_image, (400, 100))
		pygame.display.flip()

		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()
				if event.type == pygame.MOUSEBUTTONUP:
					for i in range(0, 12):
						if sobuttons.buttons[i].isOver():
						#	sobuttons.clickMusicPlay()
							if i + 1 < 10:
								self.InitMap('Sokoban0' + str(i + 1))
							else:
								self.InitMap('Sokoban' + str(i + 1))
							return
			
#			self.screen.blit(self.bnb.background, (0,0))

			sobuttons.render(self.screen)	

			pygame.display.flip()


	def check_events(self, gmbuttons):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_RIGHT: self.character.moving_right = True
				elif event.key == pygame.K_LEFT: self.character.moving_left = True
				elif event.key == pygame.K_UP: self.character.moving_up = True
				elif event.key == pygame.K_DOWN: self.character.moving_down = True
				if event.key == pygame.K_SPACE:	self.character.space = True
				if event.key == pygame.K_LCTRL: self.character.ctrl = True

			elif event.type == pygame.KEYUP:
				if event.key == pygame.K_RIGHT: self.character.moving_right = False
				elif event.key == pygame.K_LEFT: self.character.moving_left = False
				elif event.key == pygame.K_UP: self.character.moving_up = False
				elif event.key == pygame.K_DOWN: self.character.moving_down = False
				if event.key == pygame.K_SPACE and not self.character.blue_devil:	
					self.character.space = False
				if event.key == pygame.K_LCTRL: self.character.ctrl = False

			elif event.type == pygame.MOUSEBUTTONUP:
				if gmbuttons.buttons[0].isOver():	# 重新开始
	#				gmbuttons.clickMusicPlay()
					self.InitMap(self.plat.map_id)
				elif gmbuttons.buttons[1].isOver():	# 返回菜单
	#				gmbuttons.clickMusicPlay()
					self.result = 'return'


	def update_screen(self, gmbuttons):
		self.screen.fill((255,127,63))

		finished = True # 推箱子通关条件 
		
		# 绘制底层
		for y in range(len(self.plat.g[0])):
			for x in range(len(self.plat.g)):
				item = self.plat.g[x][y]
				if type(item) != bool and type(item) != plats.T:
					self.screen.blit(item.image, item.rect)
				if finished and type(item) == plats.BoxTag:
					if type(self.plat.f1[x][y]) != plats.Box:
						finished = False

		# 绘制长度为2像素的游戏边界
		pygame.draw.line(self.screen, (0, 0, 0), (15 * plats.Map.grid_len, 0 * plats.Map.grid_len), (15 * plats.Map.grid_len, 14 * plats.Map.grid_len), 2) 		
		

		#  0527版本增加：用于人物尝试使用道具
		self.character.use_prop()

		#  0527版本增加：用于道具记录榜
		self.propboard.update_use(self.character)
		self.propboard.show()

		# 绘制地图上层
		for y in range(len(self.plat.g[0])):
			for x in range(len(self.plat.g)):
				item = self.plat.f1[x][y]
				if item != None:
					self.screen.blit(item.image, item.rect)
				if type(item) == plats.Box:
					item.pushing([self.character])	# 箱子移动
					item.moving()
				if isinstance(item, bubbles.Bubble) :		# 0527版本增加：用于泡泡移动检验
					item.kick_bubble([self.character])
					item.moving()	

			for x in range(len(self.plat.g)):
				c = self.plat.c[x][y]
				for item in c:
					item.blit(self.screen)

				c = self.plat.c[x][y-1]
				for item in c:
					if type(self.plat.f1[x][y]) != plats.Obstacle:
						item.blit(self.screen)
        
        
		# 更新人物
		self.character.update()

		# 角色行动
		self.character.control()

		# 人物获取道具
		self.character.get_prop(self.propboard)

		# 人物尝试使用道具
		self.character.use_prop()

		# 用于道具记录榜
		self.propboard.update_use(self.character)
		self.propboard.show()

		# 判断推箱子游戏是否通关
		if self.plat.map_id[0:2] == 'So':
			if finished:
				kind = self.plat.map_id[:-2]
				num = int(self.plat.map_id[-2:])
				if num == 12:	# 完全通关
					congrats = pygame.image.load("images\\congrats.gif")
					congrats = pygame.transform.scale(congrats, (480, 320)).convert_alpha()
					pos = (135, 165)
					self.screen.blit(congrats, pos)
					pygame.display.flip()
					time.sleep(3)
					self.result = 'return'
				else:
					if num + 1 < 10:
						map_id = kind + '0' + str(num+1)
					else:
						map_id = kind + str(num+1)
					self.InitMap(map_id)				


		# 绘制标题
		title = pygame.image.load("images\\button\\sokoban\\" + str(int(self.plat.map_id[-2:])) + ".png")
		pos = (15 * self.plat.grid_len, 0 * self.plat.grid_len)
		self.screen.blit(title, pos)

		# 绘制按键
		gmbuttons.render(self.screen)
		
		pygame.display.flip()
