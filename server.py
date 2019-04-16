import sys
import _thread
import json
import time
import random
import numpy as np
from socket import *
from settings import *
from protocol import *
import plats
import rooms

def rand(start, end):
	random.seed()
	i = random.randint(start, end)
	return i

def rand_matrix():
	random.seed()
	i = np.random.randint(0, 99, (17, 15)).tolist()
	return i


class Server(object):
	def __init__(self):

		self.clientNO = 0
		serverName = server_name[self.clientNO]	# 定义本主机的ip
		serverPort = server_port[self.clientNO]	# 定义本主机的服务器端口

		self.serverSocket = socket(AF_INET,SOCK_STREAM)
		self.serverSocket.bind((serverName, serverPort))
		self.serverSocket.listen(1)
		print('The server is ready to work')

		self.room_ID = []
		self.room_ID_lock = _thread.allocate_lock()
		self.room_list = {}
		self.room_list_lock = _thread.allocate_lock()
		self.isInroom = {}


		self.info = [{} for i in range(0, 100)]
		self.info_lock = [_thread.allocate_lock() for i in range(0, 100)]
		self.clientNum = [0 for i in range(0, 100)]
		self.clientNum_lock = [_thread.allocate_lock() for i in range(0, 100)]
		self.clientSum = [2 for i in range(0, 100)]
		self.connectionSocket_list = [[] for i in range(0, 100)]
		self.startgame = [0 for i in range(0, 100)]
		self.startgame_lock = [_thread.allocate_lock() for i in range(0, 100)]

		self.onefunction = [False for i in range(0, 100)]
		self.onefunction_lock = [_thread.allocate_lock() for i in range(0, 100)]
		self.judging1 = False

		self.send_lock = [_thread.allocate_lock() for i in range(0, 100)]
		self.plat_id = [0 for i in range(0, 100)]
		self.props_matrix = [None for i in range(0, 100)]
		self.monst_matrix = [None for i in range(0, 100)]
		self.positions = [None for i in range(0, 100)]


	def listen(self):
		while 1:
			connectionSocket, addr = self.serverSocket.accept()
			_thread.start_new_thread(self.control, (connectionSocket, addr))


	def sendPlayerInfo(self, connectionSocket, clientNO):
		while self.isInroom[clientNO] is not False:
			send(connectionSocket, ["players_info", self.room_list[self.isInroom[clientNO]].players])
			time.sleep(0.1)


	def control(self, connectionSocket, addr):
		data = receiveSomething(connectionSocket)
		clientNO = data[0]
		self.isInroom[clientNO] = False

		while True:
			data = receiveSomething(connectionSocket)
			if type(data) == bool:
				continue
			if data[0] == "getRoom":
				sendSomething(connectionSocket, ["getRoom", self.room_ID])
				print(clientNO, "update room")
			elif data[0] == "newRoom":
				self.room_ID_lock.acquire()
				for i in range(0, 100):
					if i not in self.room_ID:
						self.room_ID.append(i)
						self.room_list_lock.acquire()
						self.room_list[i] = rooms.Room(clientNO, i)
						self.room_list[i].enter(clientNO, data[1])
						self.room_list_lock.release()
						data = [True, i]
						self.isInroom[clientNO] = data[1]
						_thread.start_new_thread(self.sendPlayerInfo, (connectionSocket, clientNO))
						print(clientNO, "create room", data[1])
						self.initGame(data[1])
						break;
					if i == 99:
						data = [False]
				self.room_ID_lock.release()
				sendSomething(connectionSocket, ["newRoom", data])
			elif data[0] == "enterRoom":
				self.room_ID_lock.acquire()
				if data[2] not in self.room_ID:
					data = [False]
				else:
					self.room_list_lock.acquire()
					self.room_list[data[2]].enter(clientNO, data[1])
					self.room_list_lock.release()
					data = [True, data[2]]
					self.isInroom[clientNO] = data[1]
					_thread.start_new_thread(self.sendPlayerInfo, (connectionSocket, clientNO))
					print(clientNO, "enter room", data[1])
				self.room_ID_lock.release()
				sendSomething(connectionSocket, data)
			elif data[0] == "exitRoom":
				self.isInroom[clientNO] = False
				self.room_ID_lock.acquire()
				self.room_list_lock.acquire()
				self.room_list[data[1]].exit(clientNO)
				if not self.room_list[data[1]].players.keys():
					self.room_list.pop(data[1])
					self.room_ID.remove(data[1])
				self.room_list_lock.release()
				self.room_ID_lock.release()
				print(clientNO, "exit room", data[1])
				sendSomething(connectionSocket, "OK")
			elif data[0] == "start":
				tmp, self.isInroom[clientNO] = self.isInroom[clientNO], False
				print(clientNO, "start game")
				self.game(data, connectionSocket)
				self.isInroom[clientNO] = tmp

			elif data[0] == "myplayer_info":
				self.room_list_lock.acquire()
				self.room_list[self.isInroom[clientNO]].enter(clientNO, data[1])
				self.room_list_lock.release()

			elif data[0] == "return room":
				_thread.start_new_thread(self.sendPlayerInfo, (connectionSocket, clientNO))


	def initGame(self, room):
		self.clientNum[room] = 0
		self.startgame[room] = 0

		self.plat_id[room] = 1#rand(0, 8)
		self.props_matrix[room] = rand_matrix()
		self.monst_matrix[room] = rand_matrix()

		try:
			filename = 'maps\\' + plats.randMap(self.plat_id[room]) + '.json'			
			with open(filename) as f_obj:
				mylist = json.load(f_obj)
				ground, floor1, info, pos, color = mylist

		except FileNotFoundError:
			print("Map File Not Found!")

		self.positions[room] = random.sample(pos, self.clientSum[room])

	def game(self, data, connectionSocket):
		client_room = data[1]
		clientNO = data[2]
		self.info_lock[client_room].acquire()
		self.info[client_room][clientNO] = {
			'name': data[3],
			'pos': self.positions[client_room][self.room_list[client_room].getPlayerPos(clientNO)],
			'color': data[4]
			}
		self.info_lock[client_room].release()
		self.connectionSocket_list[client_room].append(connectionSocket)

		self.clientNum_lock[client_room].acquire()
		self.clientNum[client_room] += 1
		self.clientNum_lock[client_room].release()

		while self.clientNum[client_room] < self.clientSum[client_room]:
			time.sleep(0.1)

		self.send_lock[client_room].acquire()

		sendSomething(connectionSocket, ["info", self.info[client_room]])
		sendSomething(connectionSocket, ["plat_id", self.plat_id[client_room]])
		sendSomething(connectionSocket, ["props_matrix", self.props_matrix[client_room]])
		sendSomething(connectionSocket, ["monst_matrix", self.monst_matrix[client_room]])

		self.startgame_lock[client_room].acquire()
		self.startgame[client_room] += 1
		self.startgame_lock[client_room].release()

		self.send_lock[client_room].release()

		while self.startgame[client_room] < self.clientSum[client_room]:
			time.sleep(0.1)

		while True:
			data = receive(connectionSocket)
			if data == False:
				continue
			elif data == ["end"]:
				print("game end", clientNO)
				send(connectionSocket, ["end"])
				break
			self.info_lock[client_room].acquire()
			self.info[client_room][clientNO] = data
			self.info_lock[client_room].release()
			self.update_client(client_room)

		self.initGame(client_room)


	# 一定要设法避免饥饿问题！！！！
	def update_client(self, client_room):
		self.onefunction_lock[client_room].acquire()
		for connectionSocket in self.connectionSocket_list[client_room]:
			self.info_lock[client_room].acquire()
			send(connectionSocket, self.info[client_room])
			self.info_lock[client_room].release()
		self.onefunction_lock[client_room].release()


if __name__ == '__main__':
	server = Server()
	server.listen()