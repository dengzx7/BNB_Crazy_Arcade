import pygame
import time
import _thread
from functions import *
import props
import plats
import bubbles
import heroes


def judge_move(item):
	# 判断是否可移动
	if item == None or item.allow_move == False:	# 判断该物体可否移动
		return False
	return True
	
class Character(heroes.Hero):
	plat = None			# 全局变量

	def __init__(self, name=None, color=None, pos=None):

		super().__init__(name, color)

		if pos == None:
			pos = self.plat.getPosition()

		self.rect = self.image.get_rect()			# 人物矩形
		self.rect.centerx = (pos[0] - 1) * self.grid_len + self.grid_len/2 + setting.offset_x
		self.rect.bottom = pos[1] * self.grid_len + setting.offset_y
		
		self.pos_x = float(self.rect.centerx - setting.offset_x)					# 浮点坐标x
		self.pos_y = float(self.rect.bottom - self.grid_len/2 - setting.offset_y)	# 浮点坐标y

		self.grid_x = pos[0]						# 整形坐标x
		self.grid_y = pos[1]						# 整形坐标y

		self.moving_right = False
		self.moving_left = False
		self.moving_up = False
		self.moving_down = False
		self.space = False
		self.ctrl = False							# ctrl触发使用道具
		self.space_force = False					# 为了解决联网中的数据丢包问题
		self.ctrl_force = False						# 为了解决联网中的数据丢包问题

		self.state = "normal"						# 定义状态：normal/block
		self.ride = False							# 是否骑宠
		self.ride_speed = 0							# 骑宠速度
		self.ride_tag = None						# 骑宠标记
		self.blue_devil = False						# 蓝魔头状态
		self.kick = False							# 踢泡泡状态
		self.prop_num = 0							# 消耗类道具数量
		self.prop_consume = None					# 当前使用的消耗类道具类型
		self.timing_bubble = None					# 当前人物已经放出的定时泡泡
		self.using_timing = False					# 是否在使用定时泡泡

		self.diedLock = _thread.allocate_lock()		# 死亡判定锁
		self.timingLock = _thread.allocate_lock()	# 定时爆炸判定锁

		self.step = 1								# 人物扭动控制
		self.previous_pos = pos						# 记录之前的位置
		self.plat.c[self.grid_x][self.grid_y].append(self)
		self.blit_count = 0							# 记录blit次数, 用于变色判定
		self.direction = "d"

	def trapped(self):
		if self.ride != False:
			self.ride = False
			self.ride_tag = None
			return
		self.state = 'trapped'
		_thread.start_new_thread(self.waiting_to_die, (0, ()))

	def waiting_to_die(self, times, i):
		self.trappedT = times
		time.sleep(1)
		self.diedLock.acquire()
		if self.state == 'trapped':
			if times == 3:
				self.burst()
			else:
				_thread.start_new_thread(self.waiting_to_die, (times + 1, ()))
		self.diedLock.release()

	def burst(self):
		self.state = 'burst'
		self.burstFrame = 0
		self.burstT = 0

	def transforward(self, forward, step):
		if self.state == 'trapped':
			return
		if self.ride == True:
			i = int(step // 25) % 2
			self.image = self.ridePic[forward][i]
		else:
			i = int(step // 20)
			self.image = self.pic[forward][i]

		if self.blue_devil and self.blit_count > 20:
			self.image = imgAnticolor(self.image)
			
		rect = self.image.get_rect()
		rect.centerx = self.rect.centerx
		rect.bottom = self.rect.bottom
		self.rect = rect

	def update(self):
		"""根据移动标志调整人物的位置"""
		if self.state == "died":
			return

		# 这个if用于控制玩家的死亡动画
		if self.state == "burst":
			self.burstT += 1
			if self.burstT == 20:
				self.burstT = 0
				self.burstFrame += 1
				if self.burstFrame == 5:
					self.state = "died"
					return
			return

		if not (self.moving_right or self.moving_left or self.moving_up or self.moving_down):
			self.transforward(self.direction, self.step)
			return

		if self.state == "trapped":
			speed = 0.25
		elif self.ride == True:
			speed = self.ride_speed
		else:
			speed = self.speed

		slide_speed = 0.25
		self.step = (self.step + speed) % 100

		# 计算网格坐标（下一时刻的位置，考虑边界重叠）
		grid_x_r = int(self.pos_x + speed + self.grid_len/2) // self.grid_len + 1		# move right
		grid_x_l = int(self.pos_x - speed - self.grid_len/2) // self.grid_len + 1		# move left
		grid_y_d = int(self.pos_y + speed + self.grid_len/2) // self.grid_len + 1		# move down
		grid_y_u = int(self.pos_y - speed - self.grid_len/2) // self.grid_len + 1		# move up

		# 右移
		if self.moving_right:
			self.direction = "r"
			if self.plat.judge_pass(grid_x_r, self.grid_y, self.ride_tag == 'f') or grid_x_r == self.grid_x:	# 后面这个or修复了人物在泡泡上部分方向不能移动的bug
				if self.pos_y < (self.grid_y - 1) * self.grid_len + self.grid_len/2 and not self.plat.judge_pass(grid_x_r, self.grid_y - 1, self.ride_tag == 'f'):  ##碰撞滑动
					self.pos_y += slide_speed
				elif self.pos_y > (self.grid_y) * self.grid_len - self.grid_len/2 and not self.plat.judge_pass(grid_x_r, self.grid_y + 1, self.ride_tag == 'f'):
					self.pos_y -= slide_speed
				else:
					self.pos_x += speed
			else:judge_moving_box(self, self.plat, (grid_x_r, self.grid_y), (1, 0))

		# 左移
		if self.moving_left:
			self.direction = "l"
			if self.plat.judge_pass(grid_x_l, self.grid_y, self.ride_tag == 'f') or grid_x_l == self.grid_x:
				if self.pos_y < (self.grid_y - 1) * self.grid_len + self.grid_len/2 and not self.plat.judge_pass(grid_x_l, self.grid_y - 1, self.ride_tag == 'f'):  ##碰撞滑动
					self.pos_y += slide_speed
				elif self.pos_y > (self.grid_y) * self.grid_len - self.grid_len/2 and not self.plat.judge_pass(grid_x_l, self.grid_y + 1, self.ride_tag == 'f'):
					self.pos_y -= slide_speed
				else:
					self.pos_x -= speed
			else:judge_moving_box(self, self.plat, (grid_x_l, self.grid_y), (-1, 0))

		# 上移
		if self.moving_up:
			self.direction = "u"
			if self.plat.judge_pass(self.grid_x, grid_y_u, self.ride_tag == 'f') or grid_y_u == self.grid_y:
				if self.pos_x < (self.grid_x - 1) * self.grid_len + self.grid_len/2 and not self.plat.judge_pass(self.grid_x - 1, grid_y_u, self.ride_tag == 'f'):		##碰撞滑动
					self.pos_x += slide_speed
				elif self.pos_x > (self.grid_x) * self.grid_len - self.grid_len/2 and not self.plat.judge_pass(self.grid_x + 1, grid_y_u, self.ride_tag == 'f'):
					self.pos_x -= slide_speed
				else:
					self.pos_y -= speed
			else:judge_moving_box(self, self.plat, (self.grid_x, grid_y_u), (0, -1))

		# 下移
		if self.moving_down:
			self.direction = "d"
			if self.plat.judge_pass(self.grid_x, grid_y_d, self.ride_tag == 'f') or grid_y_d == self.grid_y:
				if self.pos_x < (self.grid_x - 1) * self.grid_len + self.grid_len/2 and not self.plat.judge_pass(self.grid_x - 1, grid_y_d, self.ride_tag == 'f'):		##碰撞滑动
					self.pos_x += slide_speed
				elif self.pos_x > (self.grid_x) * self.grid_len - self.grid_len/2 and not self.plat.judge_pass(self.grid_x + 1, grid_y_d, self.ride_tag == 'f'):
					self.pos_x -= slide_speed
				else:
					self.pos_y += speed
			else:judge_moving_box(self, self.plat, (self.grid_x, grid_y_d), (0, 1))
		
		self.transforward(self.direction, self.step)

		self.rect.centerx = self.pos_x + setting.offset_x
		self.rect.bottom = self.pos_y + self.grid_len/2 + setting.offset_y

		# 计算网格坐标（当前人物中心位置）
		self.grid_x = int(self.pos_x) // self.grid_len + 1
		self.grid_y = int(self.pos_y) // self.grid_len + 1

		if (self.grid_x, self.grid_y) != self.previous_pos:
			self.plat.c[self.previous_pos[0]][self.previous_pos[1]].remove(self)
			self.plat.c[self.grid_x][self.grid_y].append(self)
			self.previous_pos = (self.grid_x, self.grid_y)

	def blit(self, screen):
		# 绘制人物
		if self.state == 'died':
			return
		if self.state == 'trapped':
			screen.blit(self.trappedPic[self.trappedT], self.rect)
		elif self.state == 'burst':
			screen.blit(self.burstPic[self.burstFrame], self.rect)
		elif type(self.plat.f1[self.grid_x][self.grid_y]) != plats.Shrub :   # 进入灌木躲起来
			if self.blue_devil:
				self.blit_count += 1
				if self.blit_count == 20:
					self.image = imgAnticolor(self.image)
				elif self.blit_count == 40:
					self.blit_count = 0

			screen.blit(self.image, self.rect)

	def make_bubble(self):
		if self.state not in ["normal", "Infinity"]:		return
		if self.space_force == True: return

		# 检测是否通过space键引爆定时泡泡
		if self.using_timing:
			if self.space == True:
				self.space_force = True
				_thread.start_new_thread(self.force_space, ())
				self.timingLock.release()
			return	# 使用定时泡泡时，不放正常泡泡

		# 检测是否通过space键放置正常泡泡
		if self.plat.f1[self.grid_x][self.grid_y] != None:	return
		if self.space == False or self.bubble_nums <= self.used_nums:	return
		self.plat.f1[self.grid_x][self.grid_y] = bubbles.Bubble(self)
		_thread.start_new_thread(waiting_to_explore, (self.plat.f1[self.grid_x][self.grid_y], self.plat))
		if not self.blue_devil:
			self.space_force = True
			_thread.start_new_thread(self.force_space, ())

	def make_timing_bubble(self):
		# 通过ctrl键放置定时泡泡
		if self.state not in ["normal", "Infinity"]:
			return False
		if self.plat.f1[self.grid_x][self.grid_y] != None:
			return False
		if self.ctrl_force:
			return False

		if not self.timingLock.locked():	# 多个泡泡共用一个线程锁
			self.timingLock.acquire()
		self.plat.f1[self.grid_x][self.grid_y] = bubbles.TimingBubble(self, self.timingLock)
		_thread.start_new_thread(waiting_to_explore, (self.plat.f1[self.grid_x][self.grid_y], self.plat))
		return True


	def force_space(self):
		time.sleep(0.1)
		self.space = False
		self.space_force = False

	def force_ctrl(self):
		time.sleep(0.1)
		self.ctrl = False
		self.ctrl_force = False

	def get_prop(self, propboard, board=False):
		# 人物获得道具，若道具为消耗类道具，绘制记录榜
		if not isinstance(self.plat.f1[self.grid_x][self.grid_y], props.Prop):	return
		if self.state not in ["normal", "Infinity"]:		return 
		if self.ride_tag == 'f': return
		
		# AI不获得飞碟
		if type(self.plat.f1[self.grid_x][self.grid_y]) == props.Fly and type(self) != Character:
			self.plat.f1[self.grid_x][self.grid_y] = None
			return

		self.plat.f1[self.grid_x][self.grid_y].prop_function(self)
		# AI不绘制纪录榜
		if isinstance(self.plat.f1[self.grid_x][self.grid_y], props.SpecialProp) and type(self) == Character and board:
			propboard.update_get(self.plat.f1[self.grid_x][self.grid_y], self)
		self.plat.f1[self.grid_x][self.grid_y] = None


	def use_prop(self):
		if self.prop_num > 0 and self.ctrl == True:
			self.prop_consume.consume_function(self)

	def kill(self):
		if self.state not in ["normal", "Infinity"]:		return 

		for c in self.plat.c[self.grid_x][self.grid_y]:
			if c != self and c.state == "trapped":
				c.burst()

	def control(self):
		self.make_bubble()
		self.kill()


def waiting_to_explore(bubble, plat):
	if type(plat.g[bubble.x][bubble.y]) == plats.Spine:
		bubble.explore()
	if isinstance(bubble, bubbles.TimingBubble):
		bubble.timingLock.acquire()
		bubble.character.using_timing = False
		bubble.character.space = False
		if not bubble.blast:
			bubble.explore()
		bubble.timingLock.release()

	else:
		time.sleep(3)
		if not bubble.blast:
			bubble.explore()

def judge_moving_box(character, plat, pos, dpos):
	if character.state not in ["normal", "Infinity"]:		return
	(x, y), (dx, dy) = pos, dpos
	if judge_move(plat.f1[x][y]) and plat.judge_pass(x + dx, y + dy):
		plat.f1[x][y].push_box(dx, dy)