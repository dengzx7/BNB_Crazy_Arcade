# 《外星人大战》参考代码

#-*- coding:utf-8-*-
import pygame
from sys import exit
from random import randint
from math import sqrt
pygame.init()
SCREEN_SIZE = (480,766)
screen = pygame.display.set_mode(SCREEN_SIZE,pygame.FULLSCREEN,32)
pygame.display.set_caption(" Plane Fight!")

count_b = 7
count_e = 50
fps = 100

ufo = pygame.image.load('ufo2.png').convert_alpha()
background = pygame.image.load('background.png').convert_alpha()
gameover_image = pygame.image.load('gameover.png').convert_alpha()
plane_image = pygame.image.load('hero.png').convert_alpha()
bullet_image = pygame.image.load('bullet.png').convert_alpha()
enemy_image = pygame.image.load('enemy2.png').convert_alpha()
logo = pygame.image.load('shoot_copyright.png').convert_alpha()
bomb_num = pygame.image.load('bomb_num.png').convert_alpha()
bomb_image = pygame.image.load('bomb.png').convert_alpha()
loading = []
loading.append(pygame.image.load('game_loading1.png').convert_alpha())
loading.append(pygame.image.load('game_loading2.png').convert_alpha())
loading.append(pygame.image.load('game_loading3.png').convert_alpha())
enemydown=[]
enemydown.append(pygame.image.load('enemy2_down1.png').convert_alpha())
enemydown.append(pygame.image.load('enemy2_down2.png').convert_alpha())
enemydown.append(pygame.image.load('enemy2_down3.png').convert_alpha())
enemydown.append(pygame.image.load('enemy2_down4.png').convert_alpha())
boom = []
boom.append(pygame.image.load('boom0.png').convert_alpha())
boom.append(pygame.image.load('boom1.png').convert_alpha())
boom.append(pygame.image.load('boom1.png').convert_alpha())
boom.append(pygame.image.load('boom2.png').convert_alpha())
boom.append(pygame.image.load('boom2.png').convert_alpha())

backmusic=pygame.mixer.Sound('game_music.ogg')
buttonmusic = pygame.mixer.Sound('button.ogg')
bulletmusic = pygame.mixer.Sound('bullet.wav')
enemydownmusic = pygame.mixer.Sound('enemy1_down.wav')
gameovermusic = pygame.mixer.Sound('game_over.ogg')
getbombmusic = pygame.mixer.Sound('get_bomb.wav')
usebombmusic = pygame.mixer.Sound('use_bomb.wav')

buttonmusic.set_volume(0.2)
bulletmusic.set_volume(0.04)
gameovermusic.set_volume(0.5)
enemydownmusic.set_volume(0.1)
channel = backmusic.play(-1)
channel.set_volume(0.1,0.1)
channel.pause()

font1 = pygame.font.Font(None,64)
font2 = pygame.font.Font(None,128)
clock = pygame.time.Clock()


def showLoading(count,pos):
	n = count/50
	x, y = pos
	w, h = loading[2].get_size()
	x -= w/2
	y -= h/2
	if n <3:
		screen.blit(loading[n],(x,y))

class Button(object):
	def __init__(self, upimage, downimage, position):
		self.image_up = pygame.image.load(upimage).convert_alpha()
		self.image_down = pygame.image.load(downimage).convert_alpha()
		self.position = position
		self.button_out = True

	def is_over(self):
		point_x, point_y = pygame.mouse.get_pos()
		x, y = self.position
		w, h = self.image_up.get_size()
		x -= w/2
		y -= h/2

		in_x = x < point_x < x + w
		in_y = y < point_y < y + h
		return in_x and in_y
	 
	def render(self, surface):
		x, y = self.position
		w, h = self.image_up.get_size()
		x -= w/2
		y -= h/2
		if self.is_over():
			surface.blit(self.image_down, (x, y))
			if self.button_out == True:
				buttonmusic.play()
				self.button_out = False
		else:
			surface.blit(self.image_up, (x, y))
			self.button_out = True

class Hero(object):
	def restart(self):
		self.x = 200
		self.y = 600
	def __init__(self):
		self.restart()
		self.image = plane_image
	def move(self, time_passed_seconds):
		mouseX, mouseY = pygame.mouse.get_pos()
		self.x = mouseX - self.image.get_width()/2
		self.y = mouseY - self.image.get_height()/2
	
		
class Bullet(object):    
	def __init__(self):
		self.x = 0
		self.y = -1
		self.image = bullet_image
		self.active = False
	def move(self,time_passed_seconds):
		if self.active :
			self.y -= 700 * time_passed_seconds
		if self.y < 0:
			self.active = False
			
	def restart(self,flag):
		mouseX, mouseY = pygame.mouse.get_pos()
		if flag == 1:
			self.x = mouseX - self.image.get_width()/2 
			self.y = mouseY - self.image.get_height()/2
		if flag == 2:
			self.x = mouseX - self.image.get_width()/2 + 33
			self.y = mouseY - self.image.get_height()/2
		self.active = True
class Enemy(object):
	def restart(self, score):
		self.x = randint(-30,440)
		self.y = randint(-200,-100)
		self.speed = randint(min(200+score/80,400),min(400+score/40,700))
		self.active = True
		self.count = -1
	def __init__(self,):
		self.restart(0)
		self.image = enemy_image
		self.active = False
		
	def move(self,time_passed_seconds):
		if self.y < SCREEN_SIZE[1]:
			self.y += self.speed * time_passed_seconds
		else:
			self.active = False
	def showDown(self):
		n = self.count/10
		screen.blit(enemydown[n],(self.x,self.y))
		self.count += 1
		if self.count >= 39:
			self.count = -1

class Bomb(object):
	def __init__(self):
		self.image = bomb_image
		(self.x , self.y) = (-100,-100)
		self.boom_x, self.boom_y = 0,0
		self.speed = 800
		self.active = False
		self.is_boom = False
		self.boomcount = 0
	def shoot(self):
		self.x, self.y = pygame.mouse.get_pos()
		self.x -= self.image.get_width()/2
		self.y -= self.image.get_height()/2
		self.active = True
	def move(self,time_passed_seconds):
		if self.y > 250:
			self.y -= self.speed*time_passed_seconds
		else:
			self.active = False
			self.is_boom = True
			self.boom_x, self.boom_y = self.x , self.y
			usebombmusic.play()
	def checkBoom(self,enemy):
		if enemy.x - 60 < self.x < enemy.x + enemy.image.get_width()+60\
		   and enemy.y < self.y < enemy.y + enemy.image.get_height():
			self.active = False
			self.is_boom = True
			self.boom_x, self.boom_y = self.x , self.y
			usebombmusic.play()
	def checkHit(self,enemy):
		a = float(self.x - (enemy.x + enemy.image.get_width()/2))
		b = float(self.y - (enemy.y + enemy.image.get_height()/2))
		l = sqrt(a**2 + b**2)
		if l < 250:
			enemy.active = False
			enemy.count = 1
			return True
		else:
			return False
	def boom(self):
		n = self.boomcount/10
		screen.blit(boom[n],(self.boom_x-boom[n].get_width()/2, self.boom_y-boom[n].get_height()/2))
		self.boomcount += 1
		if self.boomcount >= 49:
			self.is_boom = False
			self.boomcount = 0

class Ufo(object):
	def restart(self):
		self.x = randint(-30,440)
		self.y = -107
		self.speed = 250
	def __init__(self):
		self.image = ufo
		self.restart()
		self.active = False
	def move(self,time_passed_seconds):
		if self.y < SCREEN_SIZE[1]:
			self.y += self.speed * time_passed_seconds
		else:
			self.active = False
	def checkGet(self,plane):
		if plane.x - 60 < self.x < plane.x + plane.image.get_width()+60\
		   and plane.y -80 < self.y < plane.y + plane.image.get_height():
			self.active = False
			getbombmusic.play()
			return True
		else:
			return False
		

def checkHit(enemy,bullet):
	if enemy.x < bullet.x < enemy.x + enemy.image.get_width() \
	   and enemy.y < bullet.y < enemy.y + enemy.image.get_height():
		enemy.active = False
		bullet.active = False
		enemydownmusic.play()
		enemy.count+=1
		return True
	else:
		return False

def checkCrash(enemy,plane):
	if plane.x + 0.3*plane.image.get_width()< enemy.x + enemy.image.get_width() and\
	   enemy.x  < plane.x + 0.7*plane.image.get_width() and \
	   plane.y + 0.3*plane.image.get_height() < enemy.y + enemy.image.get_height()and\
	   enemy.y < plane.y + 0.7*plane.image.get_height():
		return True
	else:
		return False

def showWelcome(gameStart, gameOver):
	for event in pygame.event.get():
		if event.type in (pygame.QUIT, pygame.KEYDOWN):
			  pygame.quit()
			  exit()
		if event.type == pygame.MOUSEBUTTONUP:
			if gameStart.is_over():
				return False
			elif gameOver.is_over():
				pygame.quit()
				exit()
	screen.blit(background, (0,0))
	screen.blit(logo, ((SCREEN_SIZE[0]-logo.get_width())/2,100))
	gameStart.render(screen)
	gameOver.render(screen)
	return True

def run():
	sound = True
	gameStart = Button('game_start.png','game_start_down.png',(SCREEN_SIZE[0]/2,SCREEN_SIZE[1]*8/12))
	gameOver = Button('game_over.png','game_over_down.png',(SCREEN_SIZE[0]/2,SCREEN_SIZE[1]*11/12))
	gameAgain = Button('game_again.png','game_again_down.png',(SCREEN_SIZE[0]/2,SCREEN_SIZE[1]*10/12))
	gameContinue = Button('game_continue.png','game_continue_down.png',(SCREEN_SIZE[0]/2,SCREEN_SIZE[1]*9/12))
	loadingCount = 0
	while showWelcome(gameStart,gameOver):
		time_passed = clock.tick(100)
		loadingCount = (loadingCount+1) % 200
		showLoading(loadingCount,(SCREEN_SIZE[0]/2,SCREEN_SIZE[1]*19/24))
		pygame.display.update()

	pygame.mouse.set_visible(False)
	plane = Hero() 
	bullets1 = []
	bullets2 = []
	for i in range(count_b):
		bullets1.append(Bullet())
		bullets2.append(Bullet())
	index_b1 = 0
	interval_b1 = 0
	#index_b2 = 0
	#interval_b2 = 0
	enemies = []
	for i in range(count_e):
		enemies.append(Enemy())
	index_e = 0
	interval_e = 0
	ufo = Ufo()
	
	SCORE = 15000
	maxScore = 0
	BOMBnum = 3
	bomb = Bomb()
	gameover = False
	gamePause = False
	bombflag = True
	event = pygame.event.wait()
	while True:       
		time_passed = clock.tick(fps)
		time_passed_seconds = time_passed / 1000.0
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					pygame.quit()
					exit()
				if event.key == pygame.K_SPACE:
					gamePause = True
			
		if gamePause:
			channel.pause()
			pygame.mouse.set_visible(True)
			screen.blit(background,(0,0))
			screen.blit(logo, ((SCREEN_SIZE[0]-logo.get_width())/2,100))
			gameOver.render(screen)
			gameAgain.render(screen)
			gameContinue.render(screen)
			bombflag = True
			if event.type == pygame.MOUSEBUTTONUP:
				if gameOver.is_over():
					pygame.quit()
					exit()
				elif gameAgain.is_over():
					pygame.mouse.set_visible(False)
					gamePause = False
					SCORE = 0
					for e in enemies:
						e.active = False
				elif gameContinue.is_over():
					pygame.mouse.set_visible(False)
					gamePause = False    
		elif not gameover:
			if randint(1,1000)==1 and ufo.active == False:
				ufo.active = True
				ufo.restart()
			channel.unpause()
			screen.blit(background,(0,0))
			screen.blit(bomb_num,(SCREEN_SIZE[0]-160,SCREEN_SIZE[1]-65))
			text = font1.render(" x %d"%BOMBnum,1,(80,80,80))
			screen.blit(text,(SCREEN_SIZE[0]-100,SCREEN_SIZE[1]-60))
			interval_b1 -= 1
		   # interval_b2 -= 1
			interval_e -= 1
			if interval_b1 < 0:
				bullets1[index_b1].restart(1)
				interval_b1 = fps/count_b
				index_b1 = (index_b1 + 1)% count_b
				bulletmusic.play()
 
			for b in bullets1:
				if b.active:
					b.move(time_passed_seconds)
					screen.blit(b.image, (b.x,b.y))
					for e in enemies:
						if e.active:
							if checkHit(e, b):
								SCORE += 100
								
 
			if interval_e < 0:
				enemies[index_e].restart(SCORE)
				interval_e = randint(max(0,30-SCORE/250),max(7,50-SCORE/700))
				index_e = (index_e + 1)% count_e
			if event.type == pygame.MOUSEBUTTONUP and BOMBnum>0 :
				if bombflag == False and bomb.active == False:
					bomb.active = True
					bomb.shoot()
					BOMBnum -= 1
					bombflag = True
			else:
				bombflag = False        
				
			if bomb.active:
				for e in enemies:
					if e.active:
						bomb.checkBoom(e)
				bomb.move(time_passed_seconds)
				screen.blit(bomb.image,(bomb.x,bomb.y))
			if bomb.is_boom:
				bomb.boom()
				for e in enemies:
					if e.active:
						if bomb.checkHit(e):
							SCORE += 100
			for e in enemies:
				if e.active:
					if checkCrash(e,plane):
						gameover = True
					e.move(time_passed_seconds)
					screen.blit(e.image, (e.x, e.y))
				if e.count != -1:
					e.showDown()
			if ufo.active:
				ufo.move(time_passed_seconds)
				if ufo.checkGet(plane):
					BOMBnum += 1
				screen.blit(ufo.image,(ufo.x,ufo.y))
				
			plane.move(time_passed_seconds)
			screen.blit(plane.image, (plane.x,plane.y))
			text = font1.render("Score: %d"%SCORE,1,(0,0,0))
			screen.blit(text,(0,0))
		else:
			bombflag = True
			channel.pause()
			if sound == True:
				gameovermusic.play()
				sound = False
			if SCORE > maxScore:
				maxScore = SCORE
			Score = font2.render(str(SCORE),1,(50,50,50))
			mScore = font1.render(str(maxScore),1,(50,50,50))
			screen.blit(gameover_image,(0,0))
			screen.blit(mScore,(150,40))
			screen.blit(Score,(240-Score.get_width()/2, 375))
			gameAgain.render(screen)
			gameOver.render(screen)
			pygame.mouse.set_visible(True)
			if event.type == pygame.MOUSEBUTTONUP:
				if gameAgain.is_over():    
					pygame.mouse.set_visible(False)
					ufo.active = False
					gameover = False
					plane.restart()
					SCORE = 0
					sound = True
					BOMBnum = 3
					for e in enemies:
						e.active = False
				elif gameOver.is_over():
					pygame.quit()
					exit()
			
		pygame.display.update()


if __name__ == '__main__':
	run()