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
		self.initGame()

	def initGame(self):
		self.connectionSocket_list = []
		self.info = {}
		self.info_lock = _thread.allocate_lock()
		self.clientNum = 0
		self.clientNum_lock = _thread.allocate_lock()
		self.clientSum = 2

		self.startgame = 0
		self.startgame_lock = _thread.allocate_lock()

		self.onefunction = False
		self.onefunction_lock = _thread.allocate_lock()

		self.send_lock = _thread.allocate_lock()

		self.plat_id = 1#rand(0, 8)
		self.props_matrix = rand_matrix()
		self.monst_matrix = rand_matrix()

		try:
			filename = 'maps\\' + plats.randMap(self.plat_id) + '.json'			
			with open(filename) as f_obj:
				mylist = json.load(f_obj)
				ground, floor1, info, pos, color = mylist

		except FileNotFoundError:
			print("Map File Not Found!")

		self.positions = random.sample(pos, self.clientSum)


	def listen(self):
		while 1:
			connectionSocket, addr = self.serverSocket.accept()
			_thread.start_new_thread(self.control, (connectionSocket, addr))


	def sendPlayerInfo(self, connectionSocket, clientNO):
		while self.isInroom[clientNO] is not False:
			send(connectionSocket, ["players_info", self.room_list[self.isInroom[clientNO]].players])
			time.sleep(0.1)


	def control(self, connectionSocket, addr):
		self.connectionSocket_list.append(connectionSocket)
		data = receiveSomething(connectionSocket)
		clientNO = data[0]
		self.isInroom[clientNO] = False

		while True:
			data = receiveSomething(connectionSocket)
			if type(data) == bool:
				continue
			if data[0] == "getRoom":
				sendSomething(connectionSocket, self.room_ID)
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
						break;
					if i == 99:
						data = [False]
				self.room_ID_lock.release()
				sendSomething(connectionSocket, data)
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
				self.isInroom[clientNO] = False
				print(clientNO, "start game")
				sendSomething(connectionSocket, "OK")
				time.sleep(1)
				break
			elif data[0] == "myplayer_info":
				self.room_list_lock.acquire()
				self.room_list[self.isInroom[clientNO]].enter(clientNO, data[1])
				self.room_list_lock.release()


		print('hahahha')
		print('receive:', data[1])
		clientNO = data[1]
		self.info_lock.acquire()
		self.info[clientNO] = {
			'name': data[2],
			'pos': self.positions[clientNO-1],
			'color': data[3]
			}
		self.info_lock.release()

		self.clientNum_lock.acquire()
		self.clientNum += 1
		self.clientNum_lock.release()

		while self.clientNum < self.clientSum:
			time.sleep(0.1)

		self.send_lock.acquire()

		sendSomething(connectionSocket, self.info)
		sendSomething(connectionSocket, self.plat_id)
		sendSomething(connectionSocket, self.props_matrix)
		sendSomething(connectionSocket, self.monst_matrix)

		self.startgame_lock.acquire()
		self.startgame += 1
		self.startgame_lock.release()

		self.send_lock.release()

		while self.startgame < self.clientSum:
			time.sleep(0.1)

		while True:
			data = receive(connectionSocket)
			if data == False:
				continue
			self.info_lock.acquire()
			self.info[clientNO] = data
			self.info_lock.release()
			self.update_client()

		connectionSocket.close()

	# 一定要设法避免饥饿问题！！！！
	def update_client(self):
		self.onefunction_lock.acquire()
		for connectionSocket in self.connectionSocket_list:
			self.info_lock.acquire()
			send(connectionSocket, self.info)
			self.info_lock.release()
		self.onefunction_lock.release()


if __name__ == '__main__':
	server = Server()
	server.listen()