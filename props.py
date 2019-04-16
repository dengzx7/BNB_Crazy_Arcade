import pygame
import pygame.font
import _thread
import time
from functions import *

class PropBoard():
	"""记录消耗道具榜的类"""
	bg_color = (0, 255, 0)

	def __init__(self, screen):
		self.screen = screen
		self.screen_rect = screen.get_rect()
		self.text_color = (30, 30, 30)
		self.font = pygame.font.SysFont(None, 48)

		# 道具度量初始化设为None
		self.record_number = None
		self.draw_number = False

		# 道具图像初始化为None
		self.prop_image = None

		self.set_rect()

	def set_rect(self):
		prop_label = "PropLeft: "
		self.number_image = self.font.render(prop_label + str(self.record_number), True, self.text_color, PropBoard.bg_color)
		self.number_rect = self.number_image.get_rect()
		self.number_rect.right = self.screen_rect.right - 50
		self.number_rect.bottom = self.screen_rect.bottom - 50

	def update_get(self, prop, character):
		# 获得消耗类道具重绘记录榜
		self.draw_number = True
		self.record_number = character.prop_num
		self.set_rect()

		# 绘制获得的道具图像
		self.prop_image = prop.image
		self.image_rect = self.prop_image.get_rect()
		self.image_rect.centerx = 850
		self.image_rect.centery = 620

	def update_use(self, character):
		# 使用消耗类道具重绘记录磅
		self.record_number = character.prop_num
		self.set_rect()

	def show(self):
		if self.draw_number:
			self.screen.blit(self.number_image, self.number_rect)
		if self.prop_image:
			self.screen.blit(self.prop_image, self.image_rect)


#====================================
#=  所有道具的基类
#====================================
class Prop():

	grid_len = setting.grid_scale

	def __init__(self, image_file, pos, plat):
		self.image = pygame.image.load(image_file)
		self.image = pygame.transform.scale(self.image, (Prop.grid_len, Prop.grid_len)).convert_alpha()
		self.rect = offsetPos(pos)
		self.x, self.y = pos

		self.allow_pass = True
		self.allow_ruin = True
		self.plat = plat			# 全局变量

	def explore(self):
		self.plat.f1[self.x][self.y] = None


class BubbleInc(Prop):
	"""属性道具 增加泡泡数量"""

	def __init__(self, pos, plat):
		super().__init__("images\\props\\bubble.png", pos, plat)

	def prop_function(self, character):
		if character.bubble_nums < character.max_bubble_nums:
			character.bubble_nums += 1


class Fluid(Prop):
	"""属性道具 增加泡泡威力"""

	def __init__(self, pos, plat):
		super().__init__("images\\props\\fluid.png", pos, plat)

	def prop_function(self, character):
		if character.power < character.max_power:
			character.power += 1


class Roller(Prop):
	"""属性道具 增加移动速度"""

	def __init__(self, pos, plat):
		super().__init__("images\\props\\roller.png", pos, plat)

	def prop_function(self, character):
		if character.speed < character.max_speed:
			character.speed += 0.25


class SuperFluid(Prop):
	"""属性道具 将泡泡威力增加到满值"""

	def __init__(self, pos, plat):
		super().__init__("images\\props\\super_fluid.png", pos, plat)

	def prop_function(self, character):
		character.power = character.max_power


class RedDevil(Prop):
	"""红魔头 速度到最大速度，能踢开单个泡泡"""

	def __init__(self, pos, plat):
		super().__init__("images\\props\\red_devil.png", pos, plat)

	def prop_function(self, character):
		character.speed = character.max_speed
		character.kick = True


class BlueDevil(Prop):
	"""蓝魔头 自动放下所有泡泡"""

	def __init__(self, pos, plat):
		super().__init__("images\\props\\blue_devil.png", pos, plat)

	def prop_function(self, character):
		character.blue_devil = True
		character.space = True
		_thread.start_new_thread(self.waiting_to_consume, (character, ))

	def waiting_to_consume(self, character):
		time.sleep(8)
		character.space = False
		character.blue_devil = False


class Kicker(Prop):
	"""属性道具 能踢开单个泡泡"""

	def __init__(self, pos, plat):
		super().__init__("images\\props\\kicker.png", pos, plat)

	def prop_function(self, character):
		character.kick = True


#====================================
#= 特殊道具的基类，用ctrl键使用
#====================================
class SpecialProp(Prop):
	def __init__(self, image_file, pos, plat, prop_number):
		super().__init__(image_file, pos, plat)
		self.prop_number = prop_number

	def prop_function(self, character):
		character.prop_num = self.prop_number
		character.prop_consume = self

	def consume_function(self, character):
		character.prop_num -= 1
		character.ctrl_force = True
		_thread.start_new_thread(character.force_ctrl, ())


class Shield(SpecialProp):
	"""特殊道具 盾牌"""

	def __init__(self, pos, plat):
		super().__init__("images\\props\\shield.png", pos, plat, 1)

	def consume_function(self, character):
		super().consume_function(character) # 有待优化：动画
		character.state = "Infinity"
		_thread.start_new_thread(self.resume, (character, ))

	def resume(self, character):
		time.sleep(4)
		character.state = "normal"


class Needle(SpecialProp):
	"""特殊道具 针"""

	def __init__(self, pos, plat):
		super().__init__("images\\props\\needle.png", pos, plat, 2)

	def consume_function(self, character):
		if character.state == 'trapped':
			character.diedLock.acquire()
			super().consume_function(character)
			character.state = 'normal'
			character.diedLock.release()

class Timing(SpecialProp):
	"""特殊道具 定时泡泡"""

	def __init__(self, pos, plat):
		super().__init__("images\\props\\timing.png", pos, plat, 3)

	def consume_function(self, character):
		res = character.make_timing_bubble()
		if res:
			super().consume_function(character)


#====================================
#= 骑宠道具的基类
#====================================
class RideProp(Prop):
	def __init__(self, image_file, pos, plat):
		super().__init__(image_file, pos, plat)

	def prop_function(self, character, ride_speed, tag):
		if character.ride:
			return
		character.ride = True
		character.ride_speed = ride_speed
		character.ride_tag = tag
		character.ridePic = {
			'u': [loadAndTransferHeroImage("images\\hero\\" + character.name + "\\r" + tag + "u" + str(i) +".png", character.color) for i in range(0, 2)],
			'd': [loadAndTransferHeroImage("images\\hero\\" + character.name + "\\r" + tag + "d" + str(i) +".png", character.color) for i in range(0, 2)],
			'l': [loadAndTransferHeroImage("images\\hero\\" + character.name + "\\r" + tag + "l" + str(i) +".png", character.color) for i in range(0, 2)],
			'r': [loadAndTransferHeroImage("images\\hero\\" + character.name + "\\r" + tag + "r" + str(i) +".png", character.color) for i in range(0, 2)],
		}
		character.image = character.ridePic['d'][0]
		rect = character.image.get_rect()
		rect.centerx = character.rect.centerx
		rect.bottom = character.rect.bottom
		character.rect = rect


class Eagle(RideProp):
	"""骑宠类道具 鹰"""

	def __init__(self, pos, plat):
		super().__init__("images\\props\\eagle.png", pos, plat)

	def prop_function(self, character):
		super().prop_function(character, 2, 'e')


class Turtle(RideProp):
	"""骑宠类道具 龟"""

	def __init__(self, pos, plat):
		super().__init__("images\\props\\turtle.png", pos, plat)

	def prop_function(self, character):
		super().prop_function(character, 0.5, 't')


class Fly(RideProp):
	"""骑宠类道具 飞船"""

	def __init__(self, pos, plat):
		super().__init__("images\\props\\fly.png", pos, plat)

	def prop_function(self, character):
		super().prop_function(character, 4, 'f')
