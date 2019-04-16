import sys
import pygame
import time
import _thread
from socket import *
from settings import *
from protocol import *

import button
import props
import plats
import bubbles
import heroes
import characters
import players
import AIModel
import monsters
import functions

def play(clientNO):
	mode = NetMode(clientNO)
	mode.hall()

class NetMode():
	screen = None
	bnb_settings = Settings()

	def __init__(self, clientNO):
		self.clientNO = clientNO

		self.name = heroes.randHero()
		self.color = heroes.randColor()
		self.player = players.Player(self.clientNO, self.name, self.color, 0)

		nextnode = 0
		serverName = server_name[nextnode]
		serverPort = server_port[nextnode]
		self.clientSocket = socket(AF_INET, SOCK_STREAM)
		self.clientSocket.connect((serverName,serverPort))

	def hall(self):
		sendSomething(self.clientSocket, [self.clientNO])

		mybuttons = button.ButtonHall()
		rooms = button.ButtonRoomList()
		self.room_IDs = []					# 存储服务器的所有房间
		self.room_result = [False]			# 用于判定是否成功进入房间
		self.player_info = {				# 自己的信息
			"name":		self.player.name,
			"hero":		self.player.hero,
			"color":	self.player.color,
		}
		while True:
			self.screen.fill((100, 200, 200))
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()
				if event.type == pygame.MOUSEBUTTONUP:
					if mybuttons.buttons[0].isOver():	# 更新房间列表
						self.getRoom()
						print("hall - 0 : update room")
					elif mybuttons.buttons[1].isOver():	# 创建房间
						self.newRoom()
						print("hall - 1 : create room")
					elif mybuttons.buttons[2].isOver():	# 返回上级
						return
					else :
						for i in range(0, len(rooms.buttons)):
							if rooms.buttons[i].isOver():
								self.enterRoom(self.room_IDs[i])
								print("hall - x : try to enter room:", self.room_IDs[i])
			if self.room_result[0] is True:
				self.room_result[0] = False
				self.room(self.room_result[1])
			rooms.updateButton(self.room_IDs)
			mybuttons.render(self.screen)
			rooms.render(self.screen)
			pygame.display.update()

	def getRoom(self):
		data = ["getRoom"]
		sendSomething(self.clientSocket, data)
		self.room_IDs = receiveSomething(self.clientSocket, "getRoom")
	def newRoom(self):
		data = ["newRoom", self.player_info]
		sendSomething(self.clientSocket, data)
		self.room_result = receiveSomething(self.clientSocket, "newRoom")
		print(self.room_result)
	def enterRoom(self, ID):
		data = ["enterRoom", self.player_info, ID]
		sendSomething(self.clientSocket, data)
		self.room_result = receiveSomething(self.clientSocket)
		print(self.room_result)
	def exitRoom(self, ID):
		data = ["exitRoom", ID]
		sendSomething(self.clientSocket, data)
		data = receiveSomething(self.clientSocket)
		print("receive", data)

	def room(self, ID):
		print("I'm in room", ID, "now!")
		mybuttons = button.ButtonRoom()
		mybuttons_color = button.ButtonColor()

		room_players = {self.clientNO: self.player,}
		while True:
			sendSomething(self.clientSocket, ["myplayer_info", self.player_info])
			data = receive(self.clientSocket)
			if type(data) != bool and data[0] == "players_info":
				pos = 1
				room_players = {self.clientNO: self.player,}
				for i in data[1].keys():
					i = int(i)
					if i != self.clientNO:
						room_players[i] = players.Player(i, data[1][str(i)]['hero'], data[1][str(i)]['color'], pos)
						pos += 1

			self.screen.fill((100, 50, 50))
			for j in range(0, 2):
				for i in range(0, 4):
					pygame.draw.rect(self.screen, (0, 127, 127), (i*150+75, j*150+50, 150, 150), 3) 		
		
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()
				if event.type == pygame.MOUSEBUTTONUP:
					if mybuttons.buttons[0].isOver():	# 开始游戏
						print("room - 0 start game")
						self.start(ID)
						sendSomething(self.clientSocket, ["return room"])
						break
					elif mybuttons.buttons[1].isOver():	# 返回上级
						print("room - 1 return hall")
						self.exitRoom(ID)
						return
					else:
						for i in range(len(mybuttons_color.buttons)):
							if mybuttons_color.buttons[i].isOver():
								self.player_info['color'] = i-1
								self.player.changeColor(i-1)

			mybuttons.render(self.screen)
			mybuttons_color.render(self.screen)
			for i in room_players.values():
				i.blit(self.screen)
			pygame.display.update()

	def start(self, roomID):
		self.init()
		self.send_hello(roomID)
		self.solv()
		self.end()

	def init(self):
		# 初始化地图
		self.plat = None

		# 初始化人物
		self.chars = {}

		# 初始化怪物
		self.bleaches = []
		monsters.Bleach.bleaches = self.bleaches

		# 初始化道具记录榜
		self.propboard = props.PropBoard(self.screen)

		self.result = None	# 游戏结束的判断

		self.global_lock = _thread.allocate_lock()

	def send_hello(self, roomID):
			
		data = ["start", roomID, self.clientNO, self.name, self.color]
		sendSomething(self.clientSocket, data)

		info = receiveSomething(self.clientSocket, "info")
		print(info)
		plat_id = receiveSomething(self.clientSocket, "plat_id")
		print(plat_id)
		props_matrix = receiveSomething(self.clientSocket, "props_matrix")
		print(props_matrix)
		monst_matrix = receiveSomething(self.clientSocket, "monst_matrix")
		print(monst_matrix)

		self.plat = plats.Map(plat_id, props_matrix, monst_matrix)
		bubbles.Bubble.plat = self.plat
		characters.Character.plat = self.plat
		monsters.Monster.plat = self.plat
		monsters.Bleach.plat = self.plat

		for client in info.keys():
			client = int(client)
			self.chars[client] = characters.Character(info[str(client)]['name'], info[str(client)]['color'], info[str(client)]['pos'])

		monsters.Monster.chars = list(self.chars.values())
		monsters.Bleach.chars = list(self.chars.values())

	def solv(self):
		_thread.start_new_thread(self.updata_client, ())
		while self.result == None:
			self.global_lock.acquire()
			self.check_events()
			self.updata_server()
			self.global_lock.release()
			self.update_screen()
			self.global_lock.acquire()
			self.check_state()
			self.game_event()
			self.global_lock.release()

	def check_state(self):
		if self.chars[self.clientNO].state == 'died':
			send(self.clientSocket, ["end"])
			self.result = "lose"
		else:
			for client in self.chars.keys():
				if client != self.clientNO and self.chars[client].state != 'died':
					return
			send(self.clientSocket, ["end"])
			self.result = "win"

	def check_events(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_RIGHT: self.chars[self.clientNO].moving_right = True
				elif event.key == pygame.K_LEFT: self.chars[self.clientNO].moving_left = True
				elif event.key == pygame.K_UP: self.chars[self.clientNO].moving_up = True
				elif event.key == pygame.K_DOWN: self.chars[self.clientNO].moving_down = True
				if event.key == pygame.K_SPACE:	self.chars[self.clientNO].space = True
				if event.key == pygame.K_LCTRL: self.chars[self.clientNO].ctrl = True

			elif event.type == pygame.KEYUP:
				if event.key == pygame.K_RIGHT: self.chars[self.clientNO].moving_right = False
				elif event.key == pygame.K_LEFT: self.chars[self.clientNO].moving_left = False
				elif event.key == pygame.K_UP: self.chars[self.clientNO].moving_up = False
				elif event.key == pygame.K_DOWN: self.chars[self.clientNO].moving_down = False
				if event.key == pygame.K_SPACE and not self.chars[self.clientNO].blue_devil and not self.chars[self.clientNO].space_force:	
					self.chars[self.clientNO].space = False
				if event.key == pygame.K_LCTRL and not self.chars[self.clientNO].ctrl_force:
					self.chars[self.clientNO].ctrl = False

	def updata_server(self):

		myinfo = {
			'moving_right': self.chars[self.clientNO].moving_right,
			'moving_left': self.chars[self.clientNO].moving_left,
			'moving_up': self.chars[self.clientNO].moving_up,
			'moving_down': self.chars[self.clientNO].moving_down,
			'space': self.chars[self.clientNO].space,
			'ctrl': self.chars[self.clientNO].ctrl,
			'pos_x': self.chars[self.clientNO].pos_x,
			'pos_y': self.chars[self.clientNO].pos_y,
			'grid_x': self.chars[self.clientNO].grid_x,
			'grid_y': self.chars[self.clientNO].grid_y,
			'rect': list(self.chars[self.clientNO].rect),
		}

		if self.clientNO == 1:
			bleachesinfo = [{
				'step': bleach.step,
				'rect': list(bleach.rect),
				'pos_x': bleach.pos_x,
				'pos_y': bleach.pos_y,
				'grid_x': bleach.grid_x,
				'grid_y': bleach.grid_y,
				'state': bleach.state,
				'count': bleach.count,
				'count2': bleach.count2,
				'moving_right': bleach.moving_right,
				'moving_left': bleach.moving_left,
				'moving_up': bleach.moving_up,
				'moving_down': bleach.moving_down,
				'direction': bleach.direction,
			} for bleach in self.bleaches]
			myinfo['bleachesinfo'] = bleachesinfo

		send(self.clientSocket, myinfo)

	def updata_client(self):
		while self.result == None:
			data = receive(self.clientSocket)
			if type(data) == bool:
				continue
			if data == ["end"]:
				return
			self.global_lock.acquire()
			for client in data.keys():
				client = int(client)
				if type(data[str(client)]) == bool:
					break
				if client != self.clientNO:
					if 'moving_right' not in data[str(client)].keys():
						continue
					self.chars[client].moving_right = data[str(client)]['moving_right']
					self.chars[client].moving_left = data[str(client)]['moving_left']
					self.chars[client].moving_up = data[str(client)]['moving_up']
					self.chars[client].moving_down = data[str(client)]['moving_down']
					self.chars[client].space = data[str(client)]['space']
					self.chars[client].ctrl = data[str(client)]['ctrl']
					self.chars[client].pos_x = data[str(client)]['pos_x']
					self.chars[client].pos_y = data[str(client)]['pos_y']
					self.chars[client].grid_x = data[str(client)]['grid_x']
					self.chars[client].grid_y = data[str(client)]['grid_y']
					self.chars[client].rect = pygame.Rect(data[str(client)]['rect'])
				if client == 1 and self.clientNO != 1:
					for i in range(0, len(self.bleaches)-1):
						self.bleaches[i].moving_right = data[str(client)]['bleachesinfo'][i]['moving_right']
						self.bleaches[i].moving_left = data[str(client)]['bleachesinfo'][i]['moving_left']
						self.bleaches[i].moving_up = data[str(client)]['bleachesinfo'][i]['moving_up']
						self.bleaches[i].moving_down = data[str(client)]['bleachesinfo'][i]['moving_down']
						self.bleaches[i].direction = data[str(client)]['bleachesinfo'][i]['direction']
						self.bleaches[i].step = data[str(client)]['bleachesinfo'][i]['step']
						self.bleaches[i].rect = pygame.Rect(data[str(client)]['bleachesinfo'][i]['rect'])
						self.bleaches[i].state = data[str(client)]['bleachesinfo'][i]['state']
						self.bleaches[i].count = data[str(client)]['bleachesinfo'][i]['count']
						self.bleaches[i].count2 = data[str(client)]['bleachesinfo'][i]['count2']
						self.bleaches[i].pos_x = data[str(client)]['bleachesinfo'][i]['pos_x']
						self.bleaches[i].pos_y = data[str(client)]['bleachesinfo'][i]['pos_y']
						self.bleaches[i].grid_x = data[str(client)]['bleachesinfo'][i]['grid_x']
						self.bleaches[i].grid_y = data[str(client)]['bleachesinfo'][i]['grid_y']
			self.global_lock.release()

	def update_screen(self):

		self.screen.fill(self.plat.color)

		for y in range(len(self.plat.g[0])):
			for x in range(len(self.plat.g)):
				item = self.plat.g[x][y]
				if type(item) != bool:
					self.screen.blit(item.image, item.rect)

		for y in range(len(self.plat.g[0])):
			for x in range(len(self.plat.g)):
				item = self.plat.f1[x][y]
				if item != None:
					self.screen.blit(item.image, item.rect)
				if type(item) == plats.Box:
					item.pushing(self.chars.values())
					item.moving()					# 箱子移动
				if isinstance(item, bubbles.Bubble) :
					item.kick_bubble(self.chars.values())
					item.moving()

			for x in range(len(self.plat.g)):
				c = self.plat.c[x][y]
				for unit in c:
					unit.blit(self.screen)

				c = self.plat.c[x-1][y-1]
				for unit in c:
					if isinstance(unit, characters.Character) and unit.ride_tag == 'f' and type(self.plat.f1[x][y]) != plats.Obstacle:
						unit.blit(self.screen)

		for y in range(len(self.plat.g[0])):
			for x in range(len(self.plat.g)):
				c = self.plat.c[x][y]
				for unit in c:
					if isinstance(unit, monsters.Bleach):
						unit.blit(self.screen)


		# 用于道具记录榜
		self.propboard.update_use(self.chars[self.clientNO])
		self.propboard.show()

		pygame.display.flip()


	def game_event(self):

		for client in self.chars.keys():
			# 更新人物
			self.chars[client].update()

			# 角色行动
			self.chars[client].make_bubble()
			self.chars[client].kill()

			# 处理道具
			self.chars[client].get_prop(self.propboard, client == self.clientNO)
			self.chars[client].use_prop()

		for bleach in self.bleaches:
			bleach.control()


	def end(self):
		print(time.clock())
		self.screen.blit(functions.imgGray(self.screen), (0, 0))
		print(time.clock())
		image = "images\\UI\\gameover\\" + self.result + ".png"
		image = pygame.image.load(image).convert_alpha()
		self.screen.blit(image, (100, 50))
		pygame.display.flip()
		time.sleep(2)