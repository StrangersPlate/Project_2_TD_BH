# -*- coding: utf-8 -*-
import pygame
import os
from subprocess import call

f = open('resolution.txt', 'r')
pygame.init()
size = width, height = [int(a) for a in f.read().split('x')]

pygame.init()
# Пока что игра будет автоматически запускаться в full-screen. Потом, возможно, стоит добавить настройку
# разрешения.
fps = 144
# Вообще было бы логично юзать 60, но у моего монитора 144 герц, гы.
fps_clock = pygame.time.Clock()
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Tower Defense Bullet Hell')
# Это временное название, честно. :)))
enemy_bullets = pygame.sprite.Group()
cursor_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
pygame.mouse.set_visible(False)
INVINCIBILITY_TIME = pygame.USEREVENT + 1
pygame.time.set_timer(INVINCIBILITY_TIME, 0)


def load_image(name, color_key=None):
    fullname = os.path.join('Data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


class Board:

    def __init__(self, cols, rows, siz, x_indent, y_indent):
        self.columns = cols
        self.rows = rows
        self.cells_data = [[0] * rows for _ in range(cols)]
        self.cell_size = siz
        self.indent = [x_indent, y_indent]
        return

    def render(self, surface):
        surface.fill((0, 0, 0))
        for i in range(self.columns):
            for j in range(self.rows):
                if self.cells_data[i][j] == 1:
                    pygame.draw.rect(surface, (0, 255, 0), (i * self.cell_size + self.indent[
                        0], j * self.cell_size + self.indent[1], self.cell_size, self.cell_size))
                pygame.draw.rect(surface, (255, 255, 255), (i * self.cell_size + self.indent[
                    0], j * self.cell_size + self.indent[1], self.cell_size, self.cell_size), 1)
        return

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        if cell:
            self.on_click(cell)
        return

    def get_cell(self, mouse_pos):
        cell = ((mouse_pos[0] - self.indent[0]) // self.cell_size, (mouse_pos[1] - self.indent[1]) // self.cell_size)
        if cell[0] >= self.columns or cell[0] < 0 or cell[1] >= self.rows or cell[1] < 0:
            return None
        return cell

    def on_click(self, cell):
        return


class Bullet(pygame.sprite.Sprite):
    image = load_image('Simple_bullet.png', -1)

    def __init__(self, current_position, speed, direction, radius, damage, *group):
        super().__init__(*group)
        self.image = pygame.transform.scale(Bullet.image, (radius + radius, radius + radius))
        self.rect = self.image.get_rect()
        self.direction = direction
        self.speed = speed / fps
        self.current_position = current_position
        self.rect.topleft = (int(self.current_position[0]), int(self.current_position[1]))
        self.coefficient = 1 / ((self.direction[0] ** 2 + self.direction[1] ** 2) ** 0.5)
        self.radius = radius
        self.colour = (255, 255, 255)
        self.mask = pygame.mask.from_surface(self.image)
        self.damage = damage
        return

    def update(self):
        current_dist = self.speed * self.coefficient
        self.current_position[0] += self.direction[0] * current_dist
        self.current_position[1] += self.direction[1] * current_dist
        self.rect.topleft = (int(self.current_position[0]), int(self.current_position[1]))
        if pygame.sprite.collide_mask(self, cursor):
            cursor.attack(self)
        return (self.current_position[0] > size[0] or self.current_position[
            0] + self.radius + self.radius < 0 or self.current_position[1] > size[1] or self.current_position[
            1] + self.radius + self.radius < 0)

    def set_pos(self, position=(-1000, -1000)):
        self.current_position = position
        self.rect.topleft = (int(self.current_position[0]), int(self.current_position[1]))
        return


class Cursor(pygame.sprite.Sprite):
    standard_image = load_image('Standard_cursor.png', -1)
    invincible_standard_image = load_image('Standard_cursor_invincible.png', -1)

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Cursor.standard_image
        self.rect = self.image.get_rect()
        self.curr_position = [0, 0]
        self.rect.topleft = (self.curr_position[0] - 16, self.curr_position[1] - 16)
        self.mask = pygame.mask.from_surface(self.image)
        self.hp = 1000
        self.invincible = False
        return

    def update(self, position):
        self.curr_position = position
        self.rect.topleft = (self.curr_position[0] - 16, self.curr_position[1] - 16)
        return

    def attack(self, bullet):
        if self.invincible:
            return
        self.hp = max(self.hp - bullet.damage, 0)
        if self.hp == 0:
            # Вызов экрана game-over.
            pass
        self.invincible = True
        self.image = Cursor.invincible_standard_image
        pygame.time.set_timer(INVINCIBILITY_TIME, 1000)
        return

    def stop_invincibility(self):
        self.invincible = False
        self.image = Cursor.standard_image
        pygame.time.set_timer(INVINCIBILITY_TIME, 0)
        return


class Enemy(pygame.sprite.Sprite):
    useless_image = load_image('Blank_image.png', -1)

    def __init__(self, speed, hp, road, *group):
        super().__init__(*group)
        self.image = Enemy.useless_image
        self.rect = self.image.get_rect()
        self.curr_position = road[0]
        self.target = 1
        self.rect.topleft = (int(self.curr_position[0]), int(self.curr_position[1]))
        self.mask = pygame.mask.from_surface(self.image)
        self.hp = hp
        self.speed = speed / fps
        self.road = road
        return

    def update(self):
        distance = self.speed
        while distance >= 0.0000000000001 and self.target < len(self.road):
            dx = self.road[self.target][0] - self.curr_position[0]
            dy = self.road[self.target][1] - self.curr_position[1]
            distance_req = (dx * dx + dy * dy) ** 0.5
            coefficient = min(distance / distance_req, 1)
            distance -= coefficient * distance_req
            if coefficient == 1:
                self.target += 1
            self.curr_position[0] += dx * coefficient
            self.curr_position[1] += dy * coefficient
        self.rect.topleft = (int(self.curr_position[0]), int(self.curr_position[1]))
        return

    def attack(self, bullet):
        self.hp = max(self.hp - bullet.damage, 0)
        if self.hp == 0:
            self.curr_position = [-1000, -1000]
        return

    def fire(self):
        return


class EnemyJack(Enemy):
    jack_image = load_image('Jack.png', -1)

    def __init__(self, road, *group):
        super().__init__(50, 1000, road, *group)
        self.image = EnemyJack.jack_image
        self.frequency = fps * 5
        self.cooldown = fps * 5

    def update(self):
        super().update()
        self.cooldown -= 1
        if self.cooldown == 0:
            self.fire()
            self.cooldown = self.frequency
        return

    def fire(self):
        directions = [[1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0], [-1, -1], [0, -1], [1, -1]]
        for direction in directions:
            bullets_list.append(Bullet([self.curr_position[0] + 24, self.curr_position[
                1] + 24], 100, direction, 8, 20, enemy_bullets))
        return


if __name__ == '__main__':
    bullets_list = []
    # Здесь хранятся все "пули"
    cursor = Cursor(cursor_group)
    enemies_list = [EnemyJack([[-100, 255], [511, 255], [511, 511], [1800, 511]], enemy_group)]
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    continue
            elif event.type == pygame.MOUSEMOTION:
                cursor.update(event.pos)
            elif event.type == INVINCIBILITY_TIME:
                cursor.stop_invincibility()
        screen.fill((0, 0, 0))
        bullet_iter = 0
        while bullet_iter < len(bullets_list):
            current_bullet = bullets_list[bullet_iter]
            if current_bullet.update():
                del bullets_list[bullet_iter]
            else:
                bullet_iter += 1
        enemy_iter = 0
        while enemy_iter < len(enemies_list):
            current_enemy = enemies_list[enemy_iter]
            if current_enemy.hp == 0:
                del enemies_list[enemy_iter]
            else:
                current_enemy.update()
                enemy_iter += 1
        enemy_bullets.draw(screen)
        cursor_group.draw(screen)
        enemy_group.draw(screen)
        pygame.display.flip()
        fps_clock.tick(fps)