import pygame
import random
import json
from functions import *
from settings import Settings


class Hero(object):

	grid_len = Settings().grid_scale

	def __init__(self, name=None, color=None):

		if name == None:
			self.name = randHero()
		else:
			self.name = name

		if color == None:
			self.color = randColor()
		else:
			self.color = color

		self.image = loadAndTransferHeroImage("images\\hero\\" + self.name + "\\pd0.png", self.color)
		self.trappedPic = [pygame.image.load("images\\hero\\" + self.name + "\\t" + str(i) + ".png") for i in range(1, 5)]
		self.trappedPic = [pygame.transform.scale(self.trappedPic[i], (self.grid_len, self.grid_len)).convert_alpha() for i in range(0, 4)]
		self.trappedT = 0							# 周期数
		self.burstPic = [loadAndTransferHeroImage("images\\hero\\" + self.name + "\\b" + str(i) + ".png", self.color)for i in range(1, 6)]
		self.burstFrame = 0							# 帧数
		self.burstT = 0								# 周期数
		self.ridePic = None
		self.pic = {
			'u': [loadAndTransferHeroImage("images\\hero\\" + self.name + "\\pu" + str(i) +".png", self.color) for i in range(0, 5)],
			'd': [loadAndTransferHeroImage("images\\hero\\" + self.name + "\\pd" + str(i) +".png", self.color) for i in range(0, 5)],
			'l': [loadAndTransferHeroImage("images\\hero\\" + self.name + "\\pl" + str(i) +".png", self.color) for i in range(0, 5)],
			'r': [loadAndTransferHeroImage("images\\hero\\" + self.name + "\\pr" + str(i) +".png", self.color) for i in range(0, 5)],
		}

		try:
			filename = 'data\\hero.json'
			with open(filename) as f_obj:
				data = json.load(f_obj)
				mydata = data[self.name]

		except FileNotFoundError:
				print("Map File Not Found!")

		self.bubble_nums = mydata[0]				# 初始泡泡数量
		self.max_bubble_nums = mydata[1]			# 最大泡泡数量
		self.used_nums = 0							# 已放泡泡数量

		self.speed = mydata[2]						# 初始速度
		self.max_speed = mydata[3]					# 最大速度

		self.power = mydata[4]						# 初始泡泡威力
		self.max_power = mydata[5]					# 最大泡泡威力

def randHero():
	names = ['bazzi', 'cappi', 'dao', 'luxcappi', 'luxmarid', 'marid']
	random.seed()
	i = random.randint(0, len(names)-1)
	return names[i]

def randColor():
	random.seed()
	i = random.randint(0, len(colorT)-1)
	return i