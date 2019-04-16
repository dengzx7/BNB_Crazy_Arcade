import pygame
import json
import random
import numpy as np
from functions import *
from settings import Settings
import props
import monsters

# 墙壁或箱子爆炸出现道具，更新plat.f1
# 后期将考虑改变概率和优化代码
def prop_appear(x, y, plat, i=None):
	if i == None:
		random.seed()
		i = np.random.randint(0, 99)
	if i < 5:  plat.f1[x][y] = None
	if  5 <= i < 30: plat.f1[x][y] = props.BubbleInc((x, y), plat)
	if 30 <= i < 35: plat.f1[x][y] = props.Fluid((x, y), plat)
	if 35 <= i < 40: plat.f1[x][y] = props.Roller((x, y), plat)
	if 40 <= i < 41: plat.f1[x][y] = props.Shield((x, y), plat)
	if 41 <= i < 50: plat.f1[x][y] = props.Needle((x, y), plat)
	if 50 <= i < 60: plat.f1[x][y] = props.SuperFluid((x, y), plat)
	if 60 <= i < 69: plat.f1[x][y] = props.Eagle((x, y), plat)
	if 69 <= i < 70: plat.f1[x][y] = props.Turtle((x, y), plat)
	if 70 <= i < 75: plat.f1[x][y] = props.BlueDevil((x, y), plat)
	if 75 <= i < 90: plat.f1[x][y] = props.RedDevil((x, y), plat)
	if 90 <= i < 91: plat.f1[x][y] = props.Kicker((x, y), plat)
	if 91 <= i < 95: plat.f1[x][y] = props.Timing((x, y), plat)
	if 95 <= i < 100: plat.f1[x][y] = props.Fly((x, y), plat)

def randMap(i=None):
	random.seed()
	if i == None:
		i = random.randint(0, 7)
	if i == 0:		return 'pirate10'
	elif i == 1:	return 'pirate00'
	elif i == 2:	return 'pirate14'
	elif i == 3:	return 'sea13'
	elif i == 4:	return 'sea18'
	elif i == 5:	return 'cemetary07'
	elif i == 6:	return 'cemetary04'
	elif i == 7:	return 'cemetary09'
	else :	return i

def monsters_appear(x, y, plat, i=None):
	if plat.map_id[:2] == 'ce':
		if i == None:
			random.seed()
			i = random.randint(0, 99)
		if i > 74:
			monsters.Bleach((x, y))
# 地图类
class Map():
	
	grid_len = setting.grid_scale
	grid_x = setting.grid_x
	grid_y = setting.grid_y

	def __init__(self, map_id=None, prop_matrix=None, mons_matrix=None):
		# 地图底层（固有属性）：界内/界外；地刺/地洞/传送带/等等
		self.g = [[not bool(i * j * (self.grid_x - i - 1) * (self.grid_y - j - 1)) for j in range(self.grid_y)] for i in range(self.grid_x)]
		
		# 地图上层：障碍物/墙壁/箱子/荫蔽/等等
		self.f1 = [[None for j in range(self.grid_y)] for i in range(self.grid_x)]

		# 地图人物层
		self.c = [[[] for j in range(self.grid_y)] for i in range(self.grid_x)]

		self.color = None

		self.pos = None

		self.map_id = randMap(map_id)

		if prop_matrix == None:
			random.seed()
			prop_matrix = np.random.randint(0, 99, (17, 15))

		if mons_matrix == None:
			random.seed()
			mons_matrix = np.random.randint(0, 99, (17, 15))

		try:
			filename = 'maps\\' + self.map_id + '.json'
			with open(filename) as f_obj:
				mylist = json.load(f_obj)
				ground, floor1, info, self.pos, self.color = mylist

		except FileNotFoundError:
				print("Map File Not Found!")

		for y in range(len(ground)):
			for x in range(len(ground[y])):
				image_file = "images\\items\\" + self.map_id[0:-2] + "\\" + ground[y][x] + ".png"
				if ground[y][x] in ['T', 'F']:
					if ground[y][x] == 'T':
						self.g[x][y] = T((x, y))
				elif ground[y][x] == 'X':
					self.g[x][y] = BoxTag((x, y))
				elif ground[y][x] == 'S':
					self.g[x][y] = Spine((x, y))
				else:
					self.g[x][y] = Item(image_file, (x, y))

				image_file = "images\\items\\" + self.map_id[0:-2] + "\\" + floor1[y][x] + ".png"
				if floor1[y][x][0] == 'o':
					self.f1[x][y] = Obstacle(image_file, (x, y), info[floor1[y][x]])
				elif floor1[y][x][0] == 'w':
					self.f1[x][y] = Wall(image_file, (x, y), info[floor1[y][x]], self, prop_matrix[x][y], mons_matrix[x][y])
				elif floor1[y][x][0] == 'b':
					self.f1[x][y] = Box(image_file, (x, y), info[floor1[y][x]], self, prop_matrix[x][y])
				elif floor1[y][x][0] == 's':
					self.f1[x][y] = Shrub(image_file, (x, y), info[floor1[y][x]], self)

	# 随机返回一个初始位置
	def getPosition(self):
		random.seed()
		i = random.randint(0, len(self.pos) - 1)
		pos = self.pos[i]
		self.pos.remove(pos)
		return pos


	# 判断是否可通行
	def judge_pass(self, x, y, fly = False):
		if isinstance(self.g[x][y], T):
			return False
		if self.f1[x][y] != None:
			return self.f1[x][y].allow_pass or fly == True and self.f1[x][y].allow_fly
		return True


# 推箱子模式地图
class SoMap(Map):
	def __init__(self, map_id):
		super().__init__(map_id)

	def getPosition(self):
		return self.pos[0]


# 基类
class Item():
	def __init__(self, image_file, pos, rect=(Map.grid_len, Map.grid_len), Yoffset=0):
		self.image = pygame.image.load(image_file)
		self.image = pygame.transform.scale(self.image, rect).convert_alpha()
		self.rect = offsetPos(pos, Yoffset)


# 建筑物类
class Building(Item):
	def __init__(self, image_file, pos, a1, a2, a3, a4, info):
		super().__init__(image_file, pos, info[0], info[1])
		self.allow_pass = a1		# 是否可通行
		self.allow_ruin = a2		# 是否可毁灭
		self.allow_move = a3		# 是否可移动
		self.allow_fly = a4			# 是否可通过飞船

# 障碍物类
class Obstacle(Building):
	def __init__(self, image_file, pos, info):
		super().__init__(image_file, pos, False, False, False, False, info)

# 墙壁类
class Wall(Building):
	def __init__(self, image_file, pos, info, plat, prop_id, mons_id):
		super().__init__(image_file, pos, False, True, False, True, info)
		self.x, self.y = pos
		self.plat = plat
		self.prop_id = prop_id
		self.mons_id = mons_id

	def explore(self):
		prop_appear(self.x, self.y, self.plat, self.prop_id)
		monsters_appear(self.x, self.y, self.plat, self.mons_id)


# 灌木类
class Shrub(Building):
	def __init__(self, image_file, pos, info, plat):
		super().__init__(image_file, pos, True, True, False, True, info)
		self.x, self.y = pos
		self.plat = plat

	def explore(self):
		self.plat.f1[self.x][self.y] = None

# 箱子类
class Box(Building):

	def __init__(self, image_file, pos, info, plat, prop_id):
		super().__init__(image_file, pos, False, True, True, True, info)
		self.x, self.y = pos
		self.image_notON = self.image
		self.image_ON = pygame.image.load(image_file[:-4] + '_.png')
		self.image_ON = pygame.transform.scale(self.image_ON, info[0]).convert_alpha()
		if type(plat.g[self.x][self.y]) == BoxTag:
			self.image = self.image_ON

		self.push_state = False		# 玩家是否在推箱子
		self.push_count = 0			# 记录玩家推箱子持续时间
		self.move_state = False		# 箱子是否在移动
		self.move_count = 0			# 记录移动的距离
		self.move_drtx = 1		# 箱子的移动方向（x轴）
		self.move_drty = 1		# 箱子的移动方向（y轴）

		self.prop_id = prop_id
		self.plat = plat

	def explore(self):
		prop_appear(self.x, self.y, self.plat, self.prop_id)

	def push_box(self, drtx, drty):
		if self.push_state == True:
			return
		self.push_state = True
		self.push_count = 0
		self.move_drtx = drtx
		self.move_drty = drty

	def pushing(self, chars):
		if self.push_state == False:
			return

		self.push_state = False
		for character in chars:
			if (character.grid_x == self.x - self.move_drtx
				and character.grid_y == self.y - self.move_drty
				and ((self.move_drtx == 1 and character.moving_right)
					or (self.move_drtx == -1 and character.moving_left)
					or (self.move_drty == 1 and character.moving_down)
					or (self.move_drty == -1 and character.moving_up))):
				self.push_state = True

		if self.push_state == False:
			return
		
		self.push_count += 1
		if self.push_count == 50:
			self.move_box()
			self.push_state = False

	def move_box(self):
		self.move_state = True
		self.move_count = 0
		self.plat.f1[self.x][self.y] = None
		self.x += self.move_drtx
		self.y += self.move_drty
		self.plat.f1[self.x][self.y] = self


	def moving(self):
		"""箱子平滑移动"""
		if self.move_state == False:
			return
		self.move_count += 1
		(x, y) = self.rect
		x += self.move_drtx
		y += self.move_drty
		self.rect = (x, y)
		if self.move_count == Map.grid_len:
			self.move_state = False

		if type(self.plat.g[self.x][self.y]) == BoxTag:
			self.image = self.image_ON
		else:
			self.image = self.image_notON

# 箱子标记
class BoxTag(Item):
	def __init__(self, pos):
		super().__init__("images\\box_tag.png", pos)

# 地刺
class Spine(Item):
	def __init__(self, pos):
		super().__init__("images\\spine.png", pos)

# 边界
class T(Item):
	def __init__(self, pos):
		super().__init__("images\\spine.png", pos)
