import pygame
from pygame.locals import *
from sys import exit

def image_rolling(screen):
    roll_color = (0, 0, 0)
    screen.fill(roll_color)

    # 对于所需要的背景图命名
    image1_filename = 'images\\about\\制作人员.png'
    image2_filename = 'images\\about\\杨仲恒.png'
    image3_filename = 'images\\about\\邓宗湘.png'
    image4_filename = 'images\\about\\张仲岳.png'
    image5_filename = 'images\\about\\姚振杰.png'


    # 将三张背景图片都加载和转化
    list_image1 = pygame.image.load(image1_filename).convert()
    list_image2 = pygame.image.load(image2_filename).convert()
    list_image3 = pygame.image.load(image3_filename).convert()
    list_image4 = pygame.image.load(image4_filename).convert()
    list_image5 = pygame.image.load(image5_filename).convert()
    
    # 生成一个image列表，后面将列表所有元素的同时向前移动一位会用到
    list_images = [list_image1, list_image2, list_image3, list_image4, list_image5]

    # 给出第一张背景图左上角的坐标
    x1, y1 = 250, 0

    while True:
        # 点击鼠标随时退出制作名单
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
               exit()
            if event.type == pygame.MOUSEBUTTONUP:
                roll_color = (0, 0, 0)
                screen.fill(roll_color)
                return

        y1 -= 0.2  # 通过改变数值能够改变滑动的速度
        if y1 <= -1200:
            roll_color = (0, 0, 0)
            screen.fill(roll_color)
            return
        # 图片滑动的算法
        screen.fill(roll_color)#防止留下轨迹，所以刷屏

        screen.blit(list_image1, (x1, y1 + 200))
        screen.blit(list_image2, (x1, y1 + 400))
        screen.blit(list_image3, (x1, y1 + 600))
        screen.blit(list_image4, (x1, y1 + 800))
        screen.blit(list_image5, (x1, y1 + 1000))

        # 使得pygame对象不断刷新
        pygame.display.flip()
