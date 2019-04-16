import pygame
from sys import exit
import os

def invertImg(rootdir, file):
	"""Inverts the colors of a pygame Screen"""
	img = pygame.image.load(rootdir + "\\" + file)
	img.lock()
	for x in range(img.get_width()):
		for y in range(img.get_height()):
			RGBA = img.get_at((x,y))
			#if RGBA[0] > 100 and RGBA[1] < 180 and RGBA[2] < 180 and -35 < RGBA[1] - RGBA[2] < 35:#bazzi
			#if RGBA[0] < 150 and RGBA[1] > 70 and RGBA[2] > 150 or RGBA[0] < 150 and RGBA[2] > 70 and 2*RGBA[1] <= RGBA[2]:#luxcappi
			#if RGBA[0] > 100 and RGBA[1] < 170 and RGBA[2] > 120:# or RGBA[0] < 150 and RGBA[2] > 70 and 2*RGBA[1] <= RGBA[2]:#dao
			#if RGBA[0] < 170 and 110 < RGBA[1] < 250 and 50 < RGBA[2] < 200 and not(RGBA[0] == 0 and RGBA[2] == 0) and not (RGBA[0] == RGBA[1] and RGBA[1] == RGBA[2]):#cappi
			if (RGBA[0] > 2*RGBA[1] or RGBA[0] == 255) and RGBA[0] > 100 and RGBA[1] < 180 and RGBA[2] < 100  and not(RGBA[0] == 0 and RGBA[2] == 0) and not (RGBA[0] == RGBA[1] and RGBA[1] == RGBA[2]):#luxcappi
				RGBA[0], RGBA[1], RGBA[2] = RGBA[0], int(RGBA[1] ** 0.7), int(RGBA[2] ** 0.7), 
				img.set_at((x,y),RGBA)

	img.unlock()
#	pygame.image.save(img, name)
	path = "images\\hero\\luxmarid-red"
	if not os.path.exists(path):
		os.mkdir(path)
	pygame.image.save(img, path + "\\" + file)
'''
invertImg("images\\surface.png")


'''
rootdir = "images\\items\\tmp"
files = os.listdir(rootdir) #列出文件夹下所有的目录与文件
for file in files:
	invertImg(rootdir, file)


