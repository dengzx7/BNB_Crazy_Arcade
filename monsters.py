import pygame
import time
import random
import _thread
from functions import *
import bubbles
import plats
import props
import characters
import AIModel

class Monster():
	grid_len = setting.grid_scale
	chars = None
	plat = None

	def __init__(self):
		self.name = "giant"
		pic = "images\\monster\\" + self.name + "\\pd0.png"
		self.image = pygame.image.load(pic).convert_alpha()
		self.speed = 1.25						# 初始速度
		self.max_speed = 2.25					# 最大速度

		pos = self.plat.getPosition()

		self.step = 1							# 人物扭动控制
		self.rect = self.image.get_rect()		# 人物矩形
		self.rect.centerx = (pos[0] - 1) * self.grid_len + self.grid_len/2 + setting.offset_x
		self.rect.bottom = pos[1] * self.grid_len + setting.offset_y

		self.pos_x = float(self.rect.centerx - setting.offset_x)		# 浮点坐标x
		self.pos_y = float(self.rect.bottom - self.grid_len/2 - setting.offset_y)	# 浮点坐标y
		self.last_x = -1
		self.last_y = -1

		self.grid_x = pos[0]  # 整形坐标x
		self.grid_y = pos[1]  # 整形坐标y

		self.moving_right = False
		self.moving_left = False
		self.moving_up = False
		self.moving_down = False

		self.state = "normal"  # 定义状态：normal/anger/kill

		self.pic = {
			'u': [pygame.image.load("images\\monster\\" + self.name + "\\pu" + str(i) + ".png").convert_alpha() for i in range(0, 4)],
			'd': [pygame.image.load("images\\monster\\" + self.name + "\\pd" + str(i) + ".png").convert_alpha() for i in range(0, 4)],
			'l': [pygame.image.load("images\\monster\\" + self.name + "\\pl" + str(i) + ".png").convert_alpha() for i in range(0, 4)],
			'r': [pygame.image.load("images\\monster\\" + self.name + "\\pr" + str(i) + ".png").convert_alpha() for i in range(0, 4)],
		}

		self.previous_pos = pos						# 记录之前的位置
		self.plat.c[self.grid_x][self.grid_y].append(self)

	def blit(self, screen):
		screen.blit(self.image, self.rect)

	def kill(self):
		for char in self.chars:
			if not isinstance(char, AIModel.AI) and char.grid_y == self.grid_y and char.grid_x == self.grid_x and char.state in ['normal', 'trapped']:
				char.burst()

	def burst(self):			#暂时没用 用于动画补充
		self.state = 'burst'
		self.burstFrame = 0
		self.burstT = 0

	def transforward(self, forward, step):
		i = int(step // 25)
		self.image = self.pic[forward][i]

		rect = self.image.get_rect()
		rect.centerx = self.rect.centerx
		rect.bottom = self.rect.bottom
		self.rect = rect

	def rand_move(self):
		a = random.randint(0, 3)
		self.moving_right = (a == 0) #False
		self.moving_left = (a == 1)
		self.moving_up = (a == 2)
		self.moving_down = (a == 3)

	def trapped(self):
		if self.state == "normal":
			self.state = "anger"
		else: self.state = "died"
		print("self.state:", self.state)

	def update(self):
		if self.state == "died": return

		speed = self.speed
		if self.state == "anger":
			speed = self.max_speed
		slide_speed = 0.25
		self.step = (self.step + speed) % 100

		# 计算网格坐标（下一时刻的位置，考虑边界重叠）
		grid_x_r = int(self.pos_x + speed + self.grid_len/2) // self.grid_len + 1  # move right
		grid_x_l = int(self.pos_x - speed - self.grid_len/2) // self.grid_len + 1  # move left
		grid_y_d = int(self.pos_y + speed + self.grid_len/2) // self.grid_len + 1  # move down
		grid_y_u = int(self.pos_y - speed - self.grid_len/2) // self.grid_len + 1  # move up

		# 右移
		if self.moving_right:
			self.transforward("r", self.step)
			if self.plat.judge_pass(grid_x_r, self.grid_y) or grid_x_r == self.grid_x:  # 后面这个or修复了人物在泡泡上部分方向不能移动的bug
				if self.pos_y < (self.grid_y - 1) * self.grid_len + self.grid_len/2 and not self.plat.judge_pass(grid_x_r, self.grid_y - 1):  ##碰撞滑动
					self.pos_y += slide_speed
				elif self.pos_y > (self.grid_y) * self.grid_len - self.grid_len/2 and not self.plat.judge_pass(grid_x_r, self.grid_y + 1):
					self.pos_y -= slide_speed
				else:
					self.pos_x += speed
		# 左移
		if self.moving_left:
			self.transforward("l", self.step)
			if self.plat.judge_pass(grid_x_l, self.grid_y) or grid_x_l == self.grid_x:
				if self.pos_y < (self.grid_y - 1) * self.grid_len + self.grid_len/2 and not self.plat.judge_pass(grid_x_l, self.grid_y - 1):  ##碰撞滑动
					self.pos_y += slide_speed
				elif self.pos_y > (self.grid_y) * self.grid_len - self.grid_len/2 and not self.plat.judge_pass(grid_x_l, self.grid_y + 1):
					self.pos_y -= slide_speed
				else:
					self.pos_x -= speed
		# 上移
		if self.moving_up:
			self.transforward("u", self.step)
			if self.plat.judge_pass(self.grid_x, grid_y_u) or grid_y_u == self.grid_y:
				if self.pos_x < (self.grid_x - 1) * self.grid_len + self.grid_len/2 and not self.plat.judge_pass(self.grid_x - 1, grid_y_u):  ##碰撞滑动
					self.pos_x += slide_speed
				elif self.pos_x > (self.grid_x) * self.grid_len - self.grid_len/2 and not self.plat.judge_pass(self.grid_x + 1, grid_y_u):
					self.pos_x -= slide_speed
				else:
					self.pos_y -= speed

		# 下移
		if self.moving_down:
			self.transforward("d", self.step)
			if self.plat.judge_pass(self.grid_x, grid_y_d) or grid_y_d == self.grid_y:
				if self.pos_x < (self.grid_x - 1) * self.grid_len + self.grid_len/2 and not self.plat.judge_pass(self.grid_x - 1, grid_y_d):  ##碰撞滑动
					self.pos_x += slide_speed
				elif self.pos_x > (self.grid_x) * self.grid_len - self.grid_len/2 and not self.plat.judge_pass(self.grid_x + 1, grid_y_d):
					self.pos_x -= slide_speed
				else:
					self.pos_y += speed

		self.rect.centerx = self.pos_x + setting.offset_x
		self.rect.bottom = self.pos_y + self.grid_len/2 + setting.offset_y

		# 计算网格坐标（当前人物中心位置）
		if self.last_x == self.pos_x and self.last_y == self.pos_y:###########如果被阻塞则换取移动方式
			self.rand_move()

		self.last_x = self.pos_x
		self.last_y = self.pos_y
		self.grid_x = int(self.pos_x) // self.grid_len + 1
		self.grid_y = int(self.pos_y) // self.grid_len + 1

		if (self.grid_x, self.grid_y) != self.previous_pos:
			self.plat.c[self.previous_pos[0]][self.previous_pos[1]].remove(self)
			self.plat.c[self.grid_x][self.grid_y].append(self)
			self.previous_pos = (self.grid_x, self.grid_y)


class Bleach(object):
	grid_len = setting.grid_scale
	plat = None
	chars = None
	bleaches = None

	def __init__(self, pos=None):
		self.name = "bleach"
		pic = "images\\monster\\" + self.name + "\\a0.png"
		self.image = pygame.image.load(pic).convert_alpha()
		self.speed = 0.5						# 初始速度
		self.max_speed = 3						# 最大速度

		if pos == None:
			pos = self.plat.getPosition()

		self.step = 1							# 人物扭动控制
		self.rect = self.image.get_rect()		# 人物矩形
		self.rect.centerx = (pos[0] - 1) * self.grid_len + self.grid_len/2 + setting.offset_x
		self.rect.bottom = pos[1] * self.grid_len + setting.offset_y

		self.pos_x = float(self.rect.centerx - setting.offset_x)		# 浮点坐标x
		self.pos_y = float(self.rect.bottom - self.grid_len/2 - setting.offset_y)	# 浮点坐标y

		self.grid_x = pos[0]  # 整形坐标x
		self.grid_y = pos[1]  # 整形坐标y

		self.state = "loading"  # 定义状态：loading/normal/anger/rush
		self.count = 0			# 记录状态时间
		self.count2 = 0			# 用于移动判定

		self.moving_right = False
		self.moving_left = False
		self.moving_up = False
		self.moving_down = False
		self.direction = 'd'

		self.pic = {
			'u': [pygame.image.load("images\\monster\\" + self.name + "\\pu" + str(i) + ".png").convert_alpha() for i in range(0, 4)],
			'd': [pygame.image.load("images\\monster\\" + self.name + "\\pd" + str(i) + ".png").convert_alpha() for i in range(0, 4)],
			'l': [pygame.image.load("images\\monster\\" + self.name + "\\pl" + str(i) + ".png").convert_alpha() for i in range(0, 4)],
			'r': [pygame.image.load("images\\monster\\" + self.name + "\\pr" + str(i) + ".png").convert_alpha() for i in range(0, 4)],
		}

		self.previous_pos = pos						# 记录之前的位置
		self.plat.c[self.grid_x][self.grid_y].append(self)
		self.bleaches.append(self)
		_thread.start_new_thread(self.appear, ())
	
	def appear(self):
		pic = [self.image] + [pygame.image.load("images\\monster\\" + self.name + "\\a" + str(i) + ".png").convert_alpha() for i in range(1, 4)] + [self.pic['u'][0]]
		for i in [0, 1, 0, 1, 1, 2, 1, 2, 1, 2, 2, 3, 2, 3, 2, 3, 3, 4, 3, 4, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4,]:
			time.sleep(0.05)
			self.image = pic[i]
			rect = self.image.get_rect()
			rect.centerx = self.rect.centerx
			rect.bottom = self.rect.bottom
			self.rect = rect
		self.state = 'normal'
		self.rand_move()

	def control(self):
		self.update()
		self.judging()
		self.kill()

	def rand_move(self):
		random.seed()
		a = random.randint(0, 3)
		self.moving_right = (a == 0) #False
		self.moving_left = (a == 1)
		self.moving_up = (a == 2)
		self.moving_down = (a == 3)

	def transforward(self, forward, step):
		if self.state == 'rush':return
		if self.state == 'anger':return
		if self.state == 'normal':
			i = int(step // 25) % 2
			self.image = self.pic[forward][i]

		rect = self.image.get_rect()
		rect.centerx = self.rect.centerx
		rect.bottom = self.rect.bottom
		self.rect = rect

	def blit(self, screen):
		screen.blit(self.image, self.rect)

	def kill(self):
		for char in self.chars:
			if not isinstance(char, AIModel.AI) and char.grid_y == self.grid_y and char.grid_x == self.grid_x and char.state in ['normal', 'trapped']:
				char.burst()

	def judging(self):
		if self.state == 'rush':
			if self.grid_x <= 2 and self.moving_left == True:
				self.count = 0
				self.state = 'normal'
				self.moving_left = False
				self.transforward("l", self.step)
			elif self.grid_y <= 2 and self.moving_up == True:
				self.count = 0
				self.state = 'normal'
				self.moving_up = False
				self.transforward("u", self.step)
			elif self.grid_x >= 14 and self.moving_right == True:
				self.count = 0
				self.state = 'normal'
				self.moving_right = False
				self.transforward("r", self.step)
			elif self.grid_y >= 12 and self.moving_down == True:
				self.count = 0
				self.state = 'normal'
				self.moving_down = False
				self.transforward("d", self.step)
			
		elif self.state == 'normal':
			self.count += 1
			if self.count <= 5000:
				self.normalMove()
			elif self.grid_y <= 3:
				self.infuriated('d')
			elif self.grid_y >= 11:
				self.infuriated('u')
			elif self.grid_x <= 3:
				self.infuriated('r')
			elif self.grid_x >= 13:
				self.infuriated('l')
			else:
				self.normalMove()

	def normalMove(self):
		self.count2 += 1
		if self.count2 < 500: return
		self.count2 = 0
		dx = self.chars[0].grid_x - self.grid_x		# 利用随机数！！！
		dy = self.chars[0].grid_y - self.grid_y
		if self.count / 500 % 10 > 4:
			self.rand_move()
		elif self.count / 500 % 10 < 3:
			self.moving_left = False
			self.moving_right = False
			self.moving_up = False
			self.moving_down = False
		elif self.count / 500 % 10 == 3:
			self.moving_left = dx < 0
			self.moving_right = dx > 0
			self.moving_up = False
			self.moving_down = False
		else:
			self.moving_left = False
			self.moving_right = False
			self.moving_up = dy < 0
			self.moving_down = dy > 0

	def infuriated(self, direction):
		self.count = 0
		self.state = 'anger'
		self.image = self.pic[direction][2]
		self.direction = direction
		_thread.start_new_thread(self.rushing, ())

	def rushing(self):
		time.sleep(1)
		self.state = 'rush'
		self.image = self.pic[self.direction][3]
		self.moving_left = self.direction == 'l'
		self.moving_right = self.direction == 'r'
		self.moving_up = self.direction == 'u'
		self.moving_down = self.direction == 'd'

	def update(self):
		if self.state in ['anger', 'loading']:
			return
		speed = self.speed
		if self.state == "rush":
			speed = self.max_speed
		self.step = (self.step + speed) % 50

		# 计算网格坐标（下一时刻的位置，考虑边界重叠）
		grid_x_r = int(self.pos_x + speed + self.grid_len/2) // self.grid_len + 1  # move right
		grid_x_l = int(self.pos_x - speed - self.grid_len/2) // self.grid_len + 1  # move left
		grid_y_d = int(self.pos_y + speed + self.grid_len/2) // self.grid_len + 1  # move down
		grid_y_u = int(self.pos_y - speed - self.grid_len/2) // self.grid_len + 1  # move up

		if self.moving_right:
			self.direction = "r"
			if grid_x_r < 16:	self.pos_x += speed

		if self.moving_left:
			self.direction = "l"
			if grid_x_l > 0:	self.pos_x -= speed

		if self.moving_up:
			self.direction = "u"
			if grid_y_u > 0:	self.pos_y -= speed

		if self.moving_down:
			self.direction = "d"
			if grid_y_d < 14:	self.pos_y += speed
		
		self.transforward(self.direction, self.step)

		self.rect.centerx = self.pos_x + setting.offset_x
		self.rect.bottom = self.pos_y + self.grid_len/2 + setting.offset_y

		self.grid_x = int(self.pos_x) // self.grid_len + 1
		self.grid_y = int(self.pos_y) // self.grid_len + 1

		if (self.grid_x, self.grid_y) != self.previous_pos:
			self.plat.c[self.previous_pos[0]][self.previous_pos[1]].remove(self)
			self.plat.c[self.grid_x][self.grid_y].append(self)
			self.previous_pos = (self.grid_x, self.grid_y)

	def trapped(self):
		return