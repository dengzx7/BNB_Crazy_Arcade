import pygame
import numpy as np
from copy import deepcopy
from characters import Character
from bubbles import Bubble
from bubbles import TimingBubble
from props import Prop
import plats


class AI(Character):
	"""
	行动策略
	所有情况下，若AI处于危险区域，躲避泡泡
	当player[]与AI不连通时，炸箱子
	当player[]与AI连通时，攻击玩家
	"""
	screen_x = 15
	screen_y = 13
	max_search_range = 70						# 最大搜索层数
	character = None
	
	def __init__(self):
		"""初始化AI"""
		super().__init__()
		self.is_AI = True						# AI
		self.evade = True						# 是否需要躲避泡泡
		self.reachable = False					# AI与玩家是否连通
		self.attack = False						# AI是否攻击玩家
		self.push = False						# AI是否需要推箱子
		self.player_pos = ()					# 最近的玩家位置
		self.box_pos = ()						# 最近的箱子位置
		self.path = []							# AI的行走路径

		# record表示当前AI获得的地图情况，True为可走，False为不可走
		self.record = [[True for j in range(self.screen_y + 1)] for i in range(self.screen_x + 1)]
		# 解决泡泡爆炸到水柱产生之间的record错误问题
		self.record_count = [[0 for j in range(self.screen_y + 1)] for i in range(self.screen_x + 1)]


	def check_record(self, x, y):
		"""检查(x, y)是否为安全区域"""
		if not (1 <= x <= self.screen_x and 1 <= y <= self.screen_y):
			return False
		return self.record[x][y]


	def check_f1(self, x, y):
		"""检查plat.f1[x][y]是否为None或Prop"""
		if not (1 <= x <= self.screen_x and 1 <= y <= self.screen_y):
			return False
		if self.plat.f1[x][y] == None or isinstance(self.plat.f1[x][y], Prop):
			return True
		return False


	def try_bubble(self, x, y):
	    """
	    判断当前位置放泡泡是否安全
	    spout_range 表示若放泡泡，该泡泡波及的范围
	    escape_range 表示若放泡泡，逃脱的范围
	    """
	    # 左右上下
	    spout_range = [0, 0, 0, 0]
	    escape_range = [0, 0, 0, 0]

	    # 计算若放泡泡，泡泡波及的范围
	    for i in range(0, 4):
	    	for j in range(1, self.power + 2):
	    		if i == 0 and not self.check_f1(x - j, y):
	    			break
	    		elif i == 1 and not self.check_f1(x + j, y):
	    			break
	    		elif i == 2 and not self.check_f1(x, y - j):
	    			break
	    		elif i == 3 and not self.check_f1(x, y + j):
	    			break
	    	if i == 0:   spout_range[i] = x - (j - 1)
	    	elif i == 1: spout_range[i] = x + (j - 1)
	    	elif i == 2: spout_range[i] = y - (j - 1)
	    	elif i == 3: spout_range[i] = y + (j - 1)

	    # 计算若放泡泡，AI的逃脱范围
	    for i in range(0, 4):
	    	for j in range(1, self.power + 2):
	    		if i == 0 and not self.check_record(x - j, y):
	    			break
	    		elif i == 1 and not self.check_record(x + j, y):
	    			break
	    		elif i == 2 and not self.check_record(x, y - j):
	    			break
	    		elif i == 3 and not self.check_record(x, y + j):
	    			break
	    	if i == 0:   escape_range[i] = x - (j - 1)
	    	elif i == 1: escape_range[i] = x + (j - 1)
	    	elif i == 2: escape_range[i] = y - (j - 1)
	    	elif i == 3: escape_range[i] = y + (j - 1)

	    # 沿着可通行的十字，人物只要可以在任意一个地方中途跳出 （-1 / +1)就说明这个泡泡不会困住人的所有逃生路径
	    for i in range(1, x - escape_range[0] + 1):
	        if self.check_record(x - i, y + 1) or self.check_record(x - i, y - 1):
	            return True

	    for i in range(1, escape_range[1] - x + 1):
	        if self.check_record(x + i, y + 1) or self.check_record(x + i, y - 1):
	            return True

	    for i in range(1, y - escape_range[2] + 1):
	        if self.check_record(x - 1, y - i) or self.check_record(x + 1, y - i):
	            return True

	    for i in range(1, escape_range[3] - y + 1):
	        if self.check_record(x - 1, y + i) or self.check_record(x + 1, y + i):
	            return True

	    # 检查泡泡威力之外有没有可通行的地方
	    for i in range(0, 4):
	    	if spout_range[i] != escape_range[i]:
	    		return False
	    if self.check_record(spout_range[0] - 1, y) or self.check_record(spout_range[1] + 1, y) or self.check_record(
	            x, spout_range[2] - 1) or self.check_record(x, spout_range[3] + 1):
	        return True
	    return False


	def compute_player_pos(self):
		"""计算距AI最近的玩家位置"""
		min = 9999
		# 二维欧式距离
		distance = np.linalg.norm(np.array((self.grid_x, self.grid_y)) - np.array((self.character.grid_x, self.character.grid_y)))
		if min > distance:
			min = distance
			self.player_pos = (self.character.grid_x, self.character.grid_y)
		if self.reachable:
			self.attack = True
		else:
			self.attack = False


	def find_path(self, option):
		"""
		BFS
		option = JudgeReachable 判断AI是否与玩家连通
		option = EvadeBubble 规避所有泡泡
		option = FindPlayer 寻找最近玩家
		option = FindBox 寻找最近箱子
		option = PushBox 计算推箱子路径
		"""
		# temp_grid[i][j] = [(), (), (), ...], 存储到达该位置的路径
		temp_grid = [[[] for j in range(self.screen_y + 1)] for i in range(self.screen_x + 1)]

		# queue = [(), (), (), ...], 存储单点位置
		queue = [(self.grid_x, self.grid_y)]

		# temp_grid[i][j] = [(), (), (), ...], 存储到达该位置的路径
		temp_grid[self.grid_x][self.grid_y].append((self.grid_x, self.grid_y))

		# visited[i][j] = bool, 存储某位置是否已遍历过
		visited = [[False for j in range(self.screen_y + 1)] for i in range(self.screen_x + 1)]

		# 记录搜索层数
		search_count = 0

		if option == "JudgeReachable":
			self.reachable = False

		while queue:
			search_count += 1
			if search_count > self.max_search_range:
				return

			cur = queue.pop(0)
			visited[cur[0]][cur[1]] = True

			# 遍历顺序 方向朝玩家
			offset = [self.player_pos[0] - self.grid_x, self.player_pos[1] - self.grid_y]
			# 右下左上
			if offset[0] >= 0 and offset[1] >= 0:
				next = [(cur[0] + 1, cur[1]), (cur[0], cur[1] + 1), (cur[0] - 1, cur[1]), (cur[0], cur[1] - 1)]
			# 右上左下
			elif offset[0] >= 0 and offset[1] < 0:
				next = [(cur[0] + 1, cur[1]), (cur[0], cur[1] - 1), (cur[0] - 1, cur[1]), (cur[0], cur[1] + 1)]
			# 左下右上
			elif offset[0] < 0 and offset[1] >= 0:
				next = [(cur[0] - 1, cur[1]), (cur[0], cur[1] + 1), (cur[0] + 1, cur[1]), (cur[0], cur[1] - 1)]
			# 左上右下
			elif offset[0] < 0 and offset[1] < 0:
				next = [(cur[0] - 1, cur[1]), (cur[0], cur[1] - 1), (cur[0] + 1, cur[1]), (cur[0], cur[1] + 1)]

			# 当遍历到目标位置时，结束
			if option == "JudgeReachable":
				if cur == self.player_pos:
					self.reachable = True
					return
			elif option == "EvadeBubble":
				if self.record[cur[0]][cur[1]]:
					self.path = temp_grid[cur[0]][cur[1]]
					return
			elif option == "FindPlayer":
				if cur == self.player_pos:
					self.path = temp_grid[cur[0]][cur[1]]
					return
			elif option == "FindBox":
				for ne in next:
					if not (1 <= ne[0] <= self.screen_x and 1 <= ne[1] <= self.screen_y):
						continue
					if (type(self.plat.f1[ne[0]][ne[1]]) == plats.Box or type(self.plat.f1[ne[0]][ne[1]]) == plats.Wall) and type(self.plat.g[cur[0]][cur[1]]) != plats.Spine:
						if not self.try_bubble(cur[0], cur[1]):
							continue
						self.path = temp_grid[cur[0]][cur[1]]
						self.box_pos = cur
						return
			elif option == "PushBox":
				for ne in next:
					if not (1 <= ne[0] <= self.screen_x and 1 <= ne[1] <= self.screen_y):
						continue
					if type(self.plat.f1[ne[0]][ne[1]]) == plats.Box:
						# c_记录cur与ne的改变量，用于指出ne在cur的哪个方向, (cur_x + 2*c_x, cur_y + 2*c_y)即为目标位置
						c_x, c_y = ne[0] - cur[0], ne[1] - cur[1]
						des_pos = (cur[0] + 2 * c_x, cur[1] + 2 * c_y)
						if not (1 <= des_pos[0] <= self.screen_x and 1 <= des_pos[1] <= self.screen_y):
							continue
						if self.plat.f1[des_pos[0]][des_pos[1]] == None or isinstance(self.plat.f1[des_pos[0]][des_pos[1]], Prop):
							temp_grid[ne[0]][ne[1]] = deepcopy(temp_grid[cur[0]][cur[1]])
							temp_grid[ne[0]][ne[1]].append(ne)
							self.path = temp_grid[ne[0]][ne[1]]
							return

			# 遍历优先顺序 下左上右
			for ne in next:
				if not (1 <= ne[0] <= self.screen_x and 1 <= ne[1] <= self.screen_y):
					continue
				if visited[ne[0]][ne[1]]:
					continue

				if option == "JudgeReachable" or option == "EvadeBubble":
					if self.plat.f1[ne[0]][ne[1]] == None or isinstance(self.plat.f1[ne[0]][ne[1]], Prop):
						queue.append(ne)
						# 需要采用深复制策略
						temp_grid[ne[0]][ne[1]] = deepcopy(temp_grid[cur[0]][cur[1]])
						temp_grid[ne[0]][ne[1]].append(ne)
				elif (option == "FindPlayer" and self.attack) or option == "FindBox" or option == "PushBox":
					if self.record[ne[0]][ne[1]]:
						queue.append(ne)
						# 需要采用深复制策略
						temp_grid[ne[0]][ne[1]] = deepcopy(temp_grid[cur[0]][cur[1]])
						temp_grid[ne[0]][ne[1]].append(ne)


	def compute_safe_region(self):
		"""计算安全区域与危险区域，存储在record中"""
		delay = 10
		for i in range(1, self.screen_x + 1):
			for j in range(1, self.screen_y + 1):
				if self.plat.f1[i][j] == None or isinstance(self.plat.f1[i][j], Prop):
					if self.record_count[i][j] >= delay:
						self.record[i][j] = True
						self.record_count[i][j] = 0
					else:
						self.record_count[i][j] += 1
				else:
					self.record[i][j] = False
					self.record_count[i][j] = 0

		for i in range(1, self.screen_x + 1):
			for j in range(1, self.screen_y + 1):
				if type(self.plat.f1[i][j]) == Bubble or type(self.plat.f1[i][j]) == TimingBubble:
				# 对泡泡四个方向的水柱区域
					for k in range(0, self.plat.f1[i][j].field + 1):
						if j - k >= 1:
							self.record[i][j - k] = False
							self.record_count[i][j - k] = 0
						if j + k <= self.screen_y:
							self.record[i][j + k] = False
							self.record_count[i][j + k] = 0
						if i - k >= 1:
							self.record[i - k][j] = False
							self.record_count[i - k][j] = 0
						if i + k <= self.screen_x:
							self.record[i + k][j] = False
							self.record_count[i + k][j] = 0


	def judge_evade(self):
		"""若AI处于危险区域，躲避泡泡"""
		if self.record[self.grid_x][self.grid_y] == False:
			self.evade = True
		else:
			self.evade = False


	def judge_push(self):
		"""若AI无路可走，推箱子"""
		if self.evade:
			return
		self.push = True
		search_count = 0

		# queue = [(), (), (), ...], 存储单点位置
		queue = [(self.grid_x, self.grid_y)]

		# visited[i][j] = bool, 存储某位置是否已遍历过
		visited = [[False for j in range(self.screen_y + 1)] for i in range(self.screen_x + 1)]

		while queue:
			search_count += 1
			if search_count > self.max_search_range:
				return

			cur = queue.pop(0)
			visited[cur[0]][cur[1]] = True

			# 终止情况
			if self.try_bubble(cur[0], cur[1]):
				self.push = False
				return

			# 遍历顺序 下左上右
			next = [(cur[0], cur[1] + 1), (cur[0] - 1, cur[1]), (cur[0], cur[1] - 1), (cur[0] + 1, cur[1])]

			for ne in next:
				if not (1 <= ne[0] <= self.screen_x and 1 <= ne[1] <= self.screen_y):
					continue
				if visited[ne[0]][ne[1]]:
					continue
				if self.check_f1(ne[0], ne[1]):
					queue.append(ne)


	def move(self):
		"""按照路径移动"""
		path_count = 0
		for des in self.path:
			# 只需取path开头部分移动
			path_count += 1
			if path_count >= 3:	break

			if (self.grid_x, self.grid_y) == des:
				self.moving_left  = False
				self.moving_right = False
				self.moving_down  = False
				self.moving_up	  = False
			else:
				move_x, move_y = des[0] - self.grid_x, des[1] - self.grid_y
				if move_x == 1:			self.moving_right = True
				if move_x == -1:		self.moving_left  = True
				if move_y == 1:			self.moving_down  = True
				if move_y == -1:		self.moving_up	  = True

		# 攻击玩家
		if self.attack:
			if (self.grid_x, self.grid_y) == self.player_pos:
				if self.try_bubble(self.grid_x, self.grid_y) == True:
					self.space = True
					self.make_bubble()
					self.space = False
		# 炸箱子
		else:
			if (self.grid_x, self.grid_y) == self.box_pos:
				self.space = True
				self.make_bubble()
				self.space = False


	def kill(self):
		if self.state not in ["normal", "Infinity"]:
			return 
		
		for c in self.plat.c[self.grid_x][self.grid_y]:
			if isinstance(c, Character) and c.state == "trapped":
				c.burst()


	def control(self):
		"""运行AI"""
		self.compute_safe_region()
		self.compute_player_pos()
		self.find_path("JudgeReachable")

		self.judge_evade()
		if self.evade:
			self.find_path("EvadeBubble")
		elif not self.attack:
			self.find_path("FindBox")
		else:
			self.find_path("FindPlayer")

		self.judge_push()
		if self.push:
			self.find_path("PushBox")

		self.move()
		self.kill()
