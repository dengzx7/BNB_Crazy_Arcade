import pygame
from sys import exit
import os
import time

# 用于去除图片格式不兼容警告
def foooooooo(name, i):
	img = pygame.image.load(name)
	# w, h = self.img.get_size()
#	img = pygame.transform.scale(img, (50, 50))
	# img = pygame.transform.scale(img, (0.8*w, 0.8*h))
	img = pygame.transform.flip(img, True, True)  # 水平和垂直翻转
	#name = name[0:-6] + 'l' + name[-5:-1] + name[-1]
	# img = pygame.transform.rotate(img, i*90) # 旋转
#	pygame.image.save(img, name[:-6] + 'p' + name[-6:])
#	print(name)
	pygame.image.save(img, name[:-4]+"_.png")
	print(name[:-4]+"_.png")

'''

foooooooo("images\\items\\sea\\r1.png", 1)


'''
rootdir = "images\\items\\tmp"
files = os.listdir(rootdir) #列出文件夹下所有的目录与文件
for file in files:
	print(file)
	foooooooo(rootdir + "\\" + file, 1)


