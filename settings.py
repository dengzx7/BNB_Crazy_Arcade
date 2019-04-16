class Settings():
	"""存储所有设置的类"""
	def __init__(self):
		"""初始化游戏的设置"""
		# 屏幕设置
		self.screen_width = 1000
		self.screen_height = 650
		self.play_width = 750
		self.play_height = 650				# 游戏主体的大小，为状态栏预留位置
		self.bg_color = (0, 122, 0)			# 绿色背景
		self.grid_scale = 40				# 格子的边长，像素为50 * 50

		self.grid_x = 15 + 2
		self.grid_y = 13 + 2				# 13 * 15 的地图

		self.offset_x = 40
		self.offset_y = 40



server_name = [
	'192.168.253.5',
#	'172.19.109.227',
#	'192.168.43.127',
	'127.0.0.1',
	'127.0.0.1',
	'127.0.0.1',
]

server_port = [
	12640,
	13744,
	15741,
	19741,
]
