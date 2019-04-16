import _thread


class Room():
	def __init__(self, player, ID):
		self.reign = player			# 房主
		self.ID = ID				# 房号
		self.players = {}			# 所有玩家
		self.room_lock = _thread.allocate_lock()	# 房间资源控制锁

	def __del__(self):
		print("room", self.ID, "deleted")

	def enter(self, player, player_info):
		self.room_lock.acquire()
		self.players[player] = player_info
		self.room_lock.release()
		
	def exit(self, player):
		self.room_lock.acquire()
		self.players.pop(player)
		self.room_lock.release()

	def getPlayerPos(self, clientNO):
		players_list = list(self.players.keys())
		players_list.sort()
		print(players_list.index(clientNO), clientNO)
		return players_list.index(clientNO)
