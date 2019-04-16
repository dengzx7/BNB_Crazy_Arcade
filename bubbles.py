import pygame
import _thread
import time
from settings import Settings
from functions import *
import props
import plats

def judge_ruin(item):
	# 判断是否可以毁灭
	if item == None:
		return True
	return item.allow_ruin

class Bubble():
	grid_len = setting.grid_scale
	screen_x = 15
	screen_y = 13
	plat = None								# 全局变量
	exploring_pool = []						# 爆炸池，管理同时爆炸的泡泡群体
	poolLock = _thread.allocate_lock()		# 爆炸池资源锁，用于控制多个泡泡同时爆炸

#	exploreLock = _thread.allocate_lock()	# 爆炸进程控制锁，这可以解决一个非常复杂的问题：
											# -- 当一个泡泡爆炸时，假设玩家处于blue_devil状态
											# -- 并且注意到泡泡的爆炸是一个子进程
											# -- 则有大概率会导致玩家在这个泡泡爆炸后立刻放下一个泡泡
											# -- 这个新放的泡泡会立即炸毁，从而导致玩家“死两次”
											# 所以必须将泡泡的爆炸视为一个原子操作
											# 但是需要传参给人物类，所以没有实现


	def __init__(self, character):
		self.image = pygame.image.load("images\\bubble.png")
		self.image = pygame.transform.scale(self.image, (self.grid_len, self.grid_len)).convert_alpha()

		self.x = character.grid_x  		# 网格横坐标
		self.y = character.grid_y  		# 网格纵坐标
		self.field = character.power	# 射程（爆炸波及网格距离）
		self.rect = offsetPos((self.x, self.y))
		self.center_pos = (self.rect[0] + int(self.grid_len / 2), self.rect[1] + int(self.grid_len / 2))
		self.character = character
		if not isinstance(self, TimingBubble):
			self.character.used_nums += 1
		self.allow_pass = False			# 不可通行
		self.allow_ruin = True			# 可毁灭
		self.allow_move = False			# 不可移动
		self.allow_fly = False
		self.blast = False				# 是否已经爆炸

		self.moving_state = False		# 移动状态
		self.mov_x = 0					# x方向移动
		self.mov_y = 0					# y方向移动
		self.des_pos = (0, 0)			# 移动目的位置
		self.moving_speed = 5			# 移动速度

	def explore(self, pool=None):

		if self.blast == True:return
		self.blast = True

		tmp = pool == None
		if tmp:
			self.poolLock.acquire()
			self.exploring_pool.append({})
			pool = self.exploring_pool[-1]
			self.poolLock.release()

		poolAddExploring(pool, (self.x, self.y), 'xy')

		for i in range(self.y - 1, self.y - self.field - 1, -1):
			if isinstance(self.plat.f1[self.x][i], Bubble):
				self.plat.f1[self.x][i].explore(pool)
			elif judge_ruin(self.plat.f1[self.x][i]):
				poolAddExploring(pool, (self.x, i), 'y')
			if self.judge_stop(self.x, i):break	# 碰壁停止

		# 下方
		for i in range(self.y + 1, self.y + self.field + 1):
			if isinstance(self.plat.f1[self.x][i], Bubble):
				self.plat.f1[self.x][i].explore(pool)
			elif judge_ruin(self.plat.f1[self.x][i]):
				poolAddExploring(pool, (self.x, i), 'y')
			if self.judge_stop(self.x, i):break

		# 左方
		for i in range(self.x - 1, self.x - self.field - 1, -1):
			if isinstance(self.plat.f1[i][self.y], Bubble):
				self.plat.f1[i][self.y].explore(pool)
			elif judge_ruin(self.plat.f1[i][self.y]):
				poolAddExploring(pool, (i, self.y), 'x')
			if self.judge_stop(i, self.y):break

		# 右方
		for i in range(self.x + 1, self.x + self.field + 1):
			if isinstance(self.plat.f1[i][self.y], Bubble):
				self.plat.f1[i][self.y].explore(pool)
			elif judge_ruin(self.plat.f1[i][self.y]):
				poolAddExploring(pool, (i, self.y), 'x')
			if self.judge_stop(i, self.y):break
	
		self.plat.f1[self.x][self.y] = None
		if tmp:	destroy(self.plat, pool)
		if not isinstance(self, TimingBubble):
			self.character.used_nums -= 1
	
	# 判断泡泡炸到某个位置是否停下
	def judge_stop(self, x, y):
		if type(self.plat.g[x][y]) == plats.T:
			return True

		item = self.plat.f1[x][y]
		if item == None or type(item) == Bubble:
			return False
		return not item.allow_pass

	def kick_bubble(self, chars):
		for character in chars:
			if character.kick == False or character.ride == True:
				continue
			# 上下左右踢泡泡
			cx = character.grid_x
			cy = character.grid_y
			if cx == self.x and cy == self.y + 1 and character.moving_up:
				self.mov_x, self.mov_y = 0, -1
			elif cx == self.x and cy == self.y - 1 and character.moving_down:
				self.mov_x, self.mov_y = 0, 1
			elif cx == self.x + 1 and cy == self.y and character.moving_left:
				self.mov_x, self.mov_y = -1, 0
			elif cx == self.x - 1 and cy == self.y and character.moving_right:
				self.mov_x, self.mov_y = 1, 0
			else:
				continue
			if (self.x + self.mov_x < 1 or self.x + self.mov_x > self.screen_x
				or self.y + self.mov_y < 1 or self.y + self.mov_y > self.screen_y
				or not self.plat.f1[self.x + self.mov_x][self.y + self.mov_y] == None):
				continue
			self.moving_state = True


	def compute_nextmove(self):
		# 计算下一目的位置
		t_x, t_y = self.x, self.y
		if (t_x + self.mov_x < 1 or t_x + self.mov_x > self.screen_x
			or t_y + self.mov_y < 1 or t_y + self.mov_y > self.screen_y
			or not self.plat.f1[t_x + self.mov_x][t_y + self.mov_y] == None):
			return
		t_x += self.mov_x
		t_y += self.mov_y
		self.des_pos = ((t_x - 0.5) * self.grid_len + setting.offset_x, (t_y - 0.5) * self.grid_len + setting.offset_y)


	def moving(self):
		# 泡泡移动
		if not self.moving_state:
			return

		self.compute_nextmove()

		self.plat.f1[self.x][self.y] = None
		# 浮点坐标
		(x, y) = self.center_pos
		x += self.mov_x * self.moving_speed
		y += self.mov_y * self.moving_speed
		self.center_pos = (x, y)
		self.rect = (x - self.grid_len // 2, y - self.grid_len // 2)

		# 网格坐标
		self.x = (x - setting.offset_x) // self.grid_len + 1
		self.y = (y - setting.offset_y) // self.grid_len + 1

		self.plat.f1[self.x][self.y] = self

		# 移动过程中碰刺爆炸
		if type(self.plat.g[self.x][self.y]) ==  plats.Spine:
			self.explore()
	
		if self.center_pos == self.des_pos:
			self.moving_state = False

def destroy(plat, pool):
	for x, y in pool.keys():
		for c in plat.c[x][y]:
			if c.state == 'normal':
				c.trapped()
		if isinstance(plat.f1[x][y], props.Prop) or plat.f1[x][y] == None:
			producing_spout(x, y, list(pool[(x, y)]), plat)
		else:
			if plat.f1[x][y].allow_ruin:
				plat.f1[x][y].explore()

	Bubble.exploring_pool.remove(pool)

# 水柱
class Spout():

	grid_len = setting.grid_scale

	def __init__(self, pos, dimension):
		if dimension == ['x']:
			self.image = pygame.image.load("images\\spoutx.bmp")

		elif dimension == ['y']:
			self.image = pygame.image.load("images\\spouty.bmp")

		else:
			self.image = pygame.image.load("images\\spout.bmp")
		
		self.image = pygame.transform.scale(self.image, (self.grid_len, self.grid_len)).convert_alpha()
		self.x = pos[0]
		self.y = pos[1]
		self.rect = offsetPos(pos)
		self.allow_pass = True			# 可通行
		self.allow_ruin = False			# 不可毁灭
		self.allow_move = False			# 不可移动


	def disappear(self):

		Bubble.plat.f1[self.x][self.y] = None

def producing_spout(x, y, dimension, plat):

	if x != 0 and y != 0 and x != setting.grid_x - 1 and y != setting.grid_y - 1:
	
		plat.f1[x][y] = Spout((x, y), dimension)

		_thread.start_new_thread(waiting_to_disappear, (plat.f1[x][y], ()))


def waiting_to_disappear(spout, i):

	time.sleep(0.5)
	
	spout.disappear()


# 定时泡泡
class TimingBubble(Bubble):
	def __init__(self, character, timingLock):
		super().__init__(character)
		self.image = pygame.image.load("images\\props\\timing_bubble.png")
		self.image = pygame.transform.scale(self.image, (self.grid_len, self.grid_len)).convert_alpha()
		self.timingLock = timingLock
		self.character.using_timing = True

	def explore(self, pool=None):
		super().explore(pool)