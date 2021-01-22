import pygame
from pygame.locals import *
import localdefs
import os
import sys
from subprocess import call

clock = pygame.time.Clock()

pygame.init()
f = open('resolution.txt', 'r')
pygame.init()
size = width, height = [int(a) for a in f.read().split('x')]
screen = pygame.display.set_mode(size)


def resolution(width, height):
    print(width, height)
    f = open('resolution.txt', 'w')
    f.write(f'{width}x{height}')
    return width, height


class Background(pygame.sprite.Sprite):
    def __init__(self, image_file, location):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image_file)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location


def main(screen, clock, size):
    width, height = size
    pygame.mouse.set_visible(True)
    run = 1
    imgs = dict()
    rects = dict()
    while run:
        screen = pygame.display.set_mode((width, height))
        bg = pygame.Surface((width, height))
        run = 1
        imgs[0] = localdefs.imgLoad('optionsimages/resolution.png')
        rects[0] = imgs[0].get_rect(centerx=width / 2, centery=height / 5)
        for num, i in enumerate(["res1", "res2", "res3"]):
            imgs[i] = localdefs.imgLoad(os.path.join("optionsimages", i + ".png"))
            rects[i] = imgs[i].get_rect(centerx=width / 2, centery=(num + 1 + 1) * height / 5)
        BackGround = Background('menuimages/background_image.png', [0, 0])
        bg.fill([255, 255, 255])
        bg.blit(pygame.transform.scale(BackGround.image, (width, height)), BackGround.rect)
        clock.tick(40)
        screen.blit(bg, (0, 0))
        for key in imgs.keys():
            screen.blit(imgs[key], rects[key])
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            elif event.type == MOUSEBUTTONUP:
                if rects["res1"].collidepoint(event.dict['pos']):
                    width, height = 800, 600
                    resolution(width, height)
                elif rects["res2"].collidepoint(event.dict['pos']):
                    width, height = 1280, 720
                    resolution(width, height)
                elif rects["res3"].collidepoint(event.dict['pos']):
                    width, height = 1240, 768
                    resolution(width, height)
            else:
                keyinput = pygame.key.get_pressed()
                if keyinput[K_ESCAPE]:
                    sys.exit()
        pygame.display.flip()


main(screen, clock, size)
