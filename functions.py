import pygame
import copy
import random
import numpy as np
import settings

setting = settings.Settings()

def loadAndTransfer(image_name, width, height):
	image = pygame.image.load(image_name)
	image = pygame.transform.scale(image, (width, height)).convert_alpha()
	return image

def imgAnticolor(image):
	img = copy.copy(image)
	img.lock()
	for x in range(img.get_width()):
		for y in range(img.get_height()):
			RGBA = img.get_at((x,y))
			for i in range(3):
				RGBA[i] = 255 - RGBA[i]
			img.set_at((x,y),RGBA)
	img.unlock()
	img.convert_alpha()
	return img

def imgGray(image):
	img = copy.copy(image)
	img.lock()
	for x in range(img.get_width()):
		for y in range(img.get_height()):
			RGBA = img.get_at((x,y))
			tmp = int((RGBA[0] + RGBA[1] + RGBA[2])/3)
			RGBA[0], RGBA[1], RGBA[2] = tmp, tmp, tmp
			img.set_at((x,y),RGBA)
	img.unlock()
	img.convert_alpha()
	return img

def poolAddExploring(pool, grid, spout_tag):
	if grid in pool:
		pool[grid] = pool[grid] | set(spout_tag)
	else:
		pool.update({grid: set(spout_tag)})

colorT = [[[0, 0.5, 0.5], [1, 0, 0], [0, 0.5, 0.5]],	# lime
	[[0, 0.5, 0.5], [0, 0.5, 0.5], [1, 0, 0]],			# blue
	[[1, 0, 0], [1, 0, 0], [0, 0.5, 0.5]],				# yellow
	[[1, 0, 0], [0, 0.5, 0.5], [1, 0, 0]],				# magenta
	[[0, 0.5, 0.5], [1, 0, 0], [1, 0, 0]],				# cyan
	[[1, 0, 0], [1, 0, 0], [1, 0, 0]],					# white
	[[0, 0.5, 0.5], [0, 0.5, 0.5], [0, 0.5, 0.5]],		# black
	[[0.75, 0, 0], [0.75, 0, 0], [0.75, 0, 0]],			# silver
	[[0.5, 0.5, 0], [0.5, 0, 0.5], [0, 0.5, 0.5]],		# olive
	[[0.5, 0.5, 0], [0, 0.5, 0.5], [0.5, 0, 0.5]],		# purple
	[[0, 0.5, 0.5], [0.5, 0.5, 0], [0.5, 0, 0.5]],		# teal
	[[0.5, 0, 0], [0, 0.5, 0.5], [0, 0.5, 0.5]],		# maroon
	[[0, 0.5, 0.5], [0.5, 0, 0], [0, 0.5, 0.5]],		# green
	[[0, 0.5, 0.5], [0, 0.5, 0.5] ,[0.5, 0, 0]],		# navy
	[[1, 0, 0], [0.75, 0.25, 0], [0.75, 0, 0.25]],		# pink
	[[1, 0, 0], [0.84, 0.08, 0.08], [0, 0.5, 0.5]],		# gold
	[[1, 0, 0], [0, 1, 0], [0, 0, 1]]
	]

def loadAndTransferHeroImage(file, color):
	img = pygame.image.load(file)
	img.lock()
	for x in range(img.get_width()):
		for y in range(img.get_height()):
			RGBA = img.get_at((x,y))
			if RGBA[0] > 100 and RGBA[1] < 180 and RGBA[2] < 180 and -35 < RGBA[1] - RGBA[2] < 35:# red
				l = [RGBA[0], RGBA[1], RGBA[2]]
				res = np.dot(l, np.transpose(colorT[color]))
				try:
					RGBA[0], RGBA[1], RGBA[2] = int(res[0]), int(res[1]), int(res[2])
				except:
					print(color, res)
				img.set_at((x,y),RGBA)
	img.unlock()
	img = img.convert_alpha()
	return img

def offsetPos(pos, Yoffset=0):
	grid_len = setting.grid_scale
	offset_x = setting.offset_x
	offset_y = setting.offset_y
	return ((pos[0] - 1) * grid_len + offset_x, (pos[1] - 1) * grid_len + offset_y + Yoffset)
