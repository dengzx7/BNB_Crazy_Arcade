import pygame
from pygame.locals import *

class MySprite(pygame.sprite.Sprite):
    def __init__(self, target):
        pygame.sprite.Sprite.__init__(self)
        self.target_surface = target		# 屏幕
        self.image = None					# 屏幕显示的图片
        self.master_image = None			# 素材图片
        self.rect = None					# self.image的位置
        self.topleft = 0,0
        self.frame = 0						# 现在的帧数
        self.old_frame = -1					# 刚才的帧数
        self.frame_width = 1
        self.frame_height = 1
        self.first_frame = 0				# 起始帧
        self.last_frame = 0					# 终止帧
        self.columns = 1					# （素材图片的）列数
        self.last_time = 0					# 用作计时

    def load(self, filename, width, height, columns):
        self.master_image = pygame.image.load(filename).convert_alpha()
        self.frame_width = width
        self.frame_height = height
        self.rect = 0,0,width,height
        self.columns = columns
        rect = self.master_image.get_rect()
        print('rect:', rect)
        self.last_frame = (rect.width // width) * (rect.height // height) - 1
        print('last_frame', self.last_frame)

    def update(self, current_time, rate=60):
        if current_time > self.last_time + rate:
            self.frame += 1
            if self.frame > self.last_frame:
                self.frame = self.first_frame
            self.last_time = current_time

        if self.frame != self.old_frame:
            frame_x = (self.frame % self.columns) * self.frame_width
            frame_y = (self.frame // self.columns) * self.frame_height
            rect = ( frame_x, frame_y, self.frame_width, self.frame_height )
            print(self.frame, rect)
            self.image = self.master_image.subsurface(rect)
            self.old_frame = self.frame

pygame.init()
screen = pygame.display.set_mode((800,600),0,32)
pygame.display.set_caption("精灵类测试")
font = pygame.font.Font(None, 18)
framerate = pygame.time.Clock()


cat = MySprite(screen)
cat.load("images\\hero\\baobao.png", 50, 50, 11)
group = pygame.sprite.Group()
group.add(cat)

while True:
    framerate.tick(30)
    ticks = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    key = pygame.key.get_pressed()
    if key[pygame.K_ESCAPE]:
        exit()
        
    screen.fill((0,0,100))

    group.update(ticks)
    group.draw(screen)
    pygame.display.update()
