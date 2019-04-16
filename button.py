import pygame
from settings import Settings

bnb_settings = Settings()

class Button(object):

	switch_sound = None
	click_sound = None

	def __init__(self, upimage, downimage, position, Mark=False, s=None):
		self.imageUp = pygame.image.load(upimage).convert_alpha()
		self.imageDown = pygame.image.load(downimage).convert_alpha()
		self.position = position
		self.button_out = True
		self.Mark = Mark
		if Mark is True:
			font = pygame.font.SysFont(None, 48)
			self.mark_image = font.render(s, True, (0, 255, 127)).convert_alpha()
			self.mark_rect = self.mark_image.get_rect()
			self.mark_rect.centerx, self.mark_rect.centery = self.position
			

	def isOver(self):
		point_x, point_y = pygame.mouse.get_pos()
		x, y = self.position
		w, h = self.imageUp.get_size()
		in_x = x - w/2 < point_x < x + w/2
		in_y = y - h/2 < point_y < y + h/2
		return in_x and in_y

	def render(self, screen):
		w, h = self.imageUp.get_size()
		x, y = self.position
		x -= w/2
		y -= h/2
		
		if self.isOver():
			screen.blit(self.imageDown, (x, y))
			if self.button_out == True:
		#		self.switch_sound.play()
				self.button_out = False
		else:
			screen.blit(self.imageUp, (x, y))
			self.button_out = True

		if self.Mark is True:
			screen.blit(self.mark_image, self.mark_rect)


sw = bnb_settings.screen_width
sh = bnb_settings.screen_height

#===================
#=  按键管理 父类
#===================
class ButtonManage(object):
	def __init__(self):
		self.buttons = None

	def render(self, screen):
		for button in self.buttons:
			button.render(screen)

	def clickMusicPlay(self):
		Button.click_sound.play()


#===================
#=  按键管理 子类
#===================
class BottonMain(ButtonManage):
	def __init__(self):
		super().__init__()
		self.buttons = [Button("images\\button\\main\\" + str(i) + ".png", "images\\button\\main\\" + str(i) + "_.png", (sw//5, sh/5*i+100)) for i in range(0, 4)]

class ButtonSokoban(ButtonManage):
	def __init__(self, bnb_settings):
		super().__init__()
		self.buttons = [Button("images\\button\\sokoban\\" + str(i) + ".png", "images\\button\\sokoban\\" + str(i) + "_.png", (sw//10+100*((i-1)%6), sh/8*((i-1)//6)+100)) for i in range(1, 13)]

class ButtonGame(ButtonManage):
	def __init__(self, bnb_settings):
		self.buttons = [Button("images\\button\\game\\" + str(i) + ".png", "images\\button\\game\\" + str(i) + "_.png", (sw//5+670, sh/5*i+50)) for i in range(0, 2)]

class ButtonHall(ButtonManage):
	def __init__(self):
		self.buttons = [Button("images\\button\\hall\\" + str(i) + ".png", "images\\button\\hall\\" + str(i) + "_.png", (sw//5, sh/5*i+20)) for i in range(1, 4)]

class ButtonRoomList(ButtonManage):
	def __init__(self):
		self.buttons = []

	def updateButton(self, room_list):
		# 此处应该将编号显示在按键上
		self.buttons = [Button("images\\button\\hall\\0.png", "images\\button\\hall\\0_.png", (sw//5*2 + 200*(i//6), 85*(i%6) + 100), True, str(room_list[i])) for i in range(len(room_list))]


class ButtonRoom(ButtonManage):
	def __init__(self):
		self.buttons = [Button("images\\button\\room\\" + str(i) + ".png", "images\\button\\room\\" + str(i) + "_.png", (sw//3+200*i, sh/6*5)) for i in range(0, 2)]

class ButtonColor(ButtonManage):
	def __init__(self):
		self.buttons = [Button("images\\button\\color\\" + str(i) + ".png", "images\\button\\color\\" + str(i) + "_.png", (750+50*(i//4), 100+50*(i%4))) for i in range(-1, 16)]
