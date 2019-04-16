import pygame
from sys import exit
import os
import numpy as np
import random

colorT = [[[0, 0.5, 0.5], [1, 0, 0], [0, 0.5, 0.5]],	#0 lime
	[[0, 0.5, 0.5], [0, 0.5, 0.5], [1, 0, 0]],			#1 blue
	[[1, 0, 0], [1, 0, 0], [0, 0.5, 0.5]],				#2 yellow
	[[1, 0, 0], [0, 0.5, 0.5], [1, 0, 0]],				#3 magenta
	[[0, 0.5, 0.5], [1, 0, 0], [1, 0, 0]],				#4 cyan
	[[1, 0, 0], [1, 0, 0], [1, 0, 0]],					#5 white
	[[0, 0.5, 0.5], [0, 0.5, 0.5], [0, 0.5, 0.5]],		#6 black
	[[0.75, 0, 0], [0.75, 0, 0], [0.75, 0, 0]],			#7 silver
	[[0.5, 0.5, 0], [0.5, 0, 0.5], [0, 0.5, 0.5]],		#8 olive
	[[0.5, 0.5, 0], [0, 0.5, 0.5], [0.5, 0, 0.5]],		#9 purple
	[[0, 0.5, 0.5], [0.5, 0.5, 0], [0.5, 0, 0.5]],		#10 teal
	[[0.5, 0, 0], [0, 0.5, 0.5], [0, 0.5, 0.5]],		#11 maroon
	[[0, 0.5, 0.5], [0.5, 0, 0], [0, 0.5, 0.5]],		#11 green
	[[0, 0.5, 0.5], [0, 0.5, 0.5] ,[0.5, 0, 0]],		#13 navy
	[[1, 0, 0], [0.75, 0.25, 0], [0.75, 0, 0.25]],		#14 pink
	[[1, 0, 0], [0.84, 0.08, 0.08], [0, 0.5, 0.5]],		#15 gold
	]

def invertImg(rootdir, file, color):
	img = pygame.image.load(rootdir+file)
	img.lock()
	for x in range(img.get_width()):
		for y in range(img.get_height()):
			RGBA = img.get_at((x,y))
			if not RGBA[0] == RGBA[1] == RGBA[2]:
				l = [RGBA[0], RGBA[1], RGBA[2]]
				res = np.dot(l, np.transpose(colorT[color]))
				RGBA[0], RGBA[1], RGBA[2] = int(res[0]), int(res[1]), int(res[2])
				img.set_at((x,y),RGBA)
	img.unlock()
	pygame.image.save(img, rootdir + str(color) + ".png")
	return img
'''
#	path = "images\\hero\\d"
#	if not os.path.exists(path):
#		os.mkdir(path)
#	pygame.image.save(img, path + "\\" + file)

invertImg("images\\surface.png")
'''

rootdir = "images\\items\\tmp"
files = os.listdir(rootdir) #列出文件夹下所有的目录与文件
for file in files:
	for i in range(11, 14):
		invertImg(rootdir + "\\", file, i)

