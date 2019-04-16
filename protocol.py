from socket import *
import json
import struct

class Protocol(object):
	def __init__(self, head, data, service = 1):

		self.data = data

		self.head = head

		if head == None:
			self.head = {
				'service': service,		# 服务类型
				'head_len': None,		# 首部长度
				'data_len': None,		# 数据长度
			}


def send(conn, data):
	data_json = json.dumps(data)
	data_bytes = data_json.encode('utf-8')

	conn.send(struct.pack('i', len(data_bytes)))	# 发送长度
	conn.send(struct.pack('i', len(data_bytes)))	# 发送长度
	conn.send(data_bytes)							# 发送数据


def receive(conn, service=None):
	data_len1 = conn.recv(4)
	data_len2 = conn.recv(4)
	if data_len1 != data_len2:
		x = conn.recv(2048)
		print('-------datalength lost error-------')
		print(x)
		return False	

	data_len = data_len1
	data_len = struct.unpack('i', data_len)[0]

	data_bytes = conn.recv(data_len)
	if data_len != len(data_bytes):
		print('-------data lost error-------')
		return False
	try:
		data_json = data_bytes.decode('utf-8')
	except UnicodeDecodeError:
		return False

	try:
		data = json.loads(data_json)
	except json.JSONDecodeError:
		return False

	if service != None:
		if type(data) == list and data[0] == service:
			return data[1]
		return False

	return data


def sendSomething(connectionSocket, data):
	send(connectionSocket, data)
	
	return_data = receive(connectionSocket)
	while return_data is not True:
		print("send packet again:", data)
		send(connectionSocket, data)
		return_data = receive(connectionSocket)

def receiveSomething(connectionSocket, service=None):
	data = receive(connectionSocket, service)	# 这个包很可能已经丢失了数据
	while type(data) is bool:
		send(connectionSocket, False)
		data = receive(connectionSocket, service)
	send(connectionSocket, True)
	return data