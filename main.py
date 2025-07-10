import os

import pygame
import math
from sys import exit
from random import randint, choice
from utils import blit_rotate_center, scale_image

pygame.init()
screen = pygame.display.set_mode((1000, 600), pygame.RESIZABLE)
pygame.display.set_caption('Room Racer')
clock = pygame.time.Clock()
game_font = pygame.font.Font('graphics/UI/Font/Kenney Future.ttf', 50)
game_active = True


asphalt_tiles = {}
ASPHALT_TILE_FOLDER = "graphics/PNG/Tiles/Asphalt road/"
TILE_SCALE = 0.5
TILE_BASE_SIZE = 256
TILE_SIZE = int(TILE_BASE_SIZE * TILE_SCALE)
GRID_WIDTH = 14
GRID_HEIGHT = 7



for filename in os.listdir(ASPHALT_TILE_FOLDER):
    if filename.endswith(".png"):
        tile_id = os.path.splitext(filename)[0].replace("road_", "")
        path = os.path.join(ASPHALT_TILE_FOLDER, filename)
        image = pygame.image.load(path).convert_alpha()
        asphalt_tiles[tile_id] = scale_image(image, 1)

class Tile:
    def __init__(self, tile_id, grid, angle=0):
        self.tile_id = tile_id
        self.grid = grid
        self.angle = angle


        TILE_WIDTH = screen.get_width() // GRID_WIDTH
        TILE_HEIGHT = screen.get_height() // GRID_HEIGHT


        raw_image = asphalt_tiles[tile_id]
        self.image = pygame.transform.scale(raw_image, (TILE_WIDTH, TILE_HEIGHT))


        self.rotated_image = pygame.transform.rotate(self.image, self.angle)


        x = grid[0] * TILE_WIDTH
        y = grid[1] * TILE_HEIGHT
        self.rect = self.rotated_image.get_rect(topleft=(x, y))

    def draw(self, surf):
        surf.blit(self.rotated_image, self.rect.topleft)


class Track:
    def __init__(self, layout_data):
        self.tiles = []
        for tile_info in layout_data:
            tile = Tile(
                tile_id=tile_info["tile"],
                grid=tuple(tile_info["grid"]),
                angle=tile_info.get("angle", 0)
            )
            self.tiles.append(tile)

    def draw(self, surf):
        for tile in self.tiles:
            tile.draw(surf)

#14 x 7
tilemap = [
    ["blank", "blank", "blank", "blank"],
    ["blank", "asphalt08", "asphalt09", "asphalt04", "asphalt04", "asphalt04", "asphalt04", "asphalt04", "asphalt04", "asphalt04", "asphalt04", "asphalt10", "asphalt11"],
    ["blank", "asphalt26", "asphalt27", "asphalt40", "asphalt40", "asphalt40", "asphalt40", "asphalt40", "asphalt40", "asphalt40", "asphalt40", "asphalt28", "asphalt29"],
    ["blank", "asphalt21", "asphalt23", "blank", "blank", "blank", "blank", "blank", "blank", "blank", "blank", "asphalt21", "asphalt23"],
    ["blank", "asphalt44", "asphalt45", "asphalt04", "asphalt04", "asphalt04", "asphalt04", "asphalt04", "asphalt04", "asphalt04", "asphalt04", "asphalt46", "asphalt47"],
    ["blank", "asphalt62", "asphalt63", "asphalt40", "asphalt40", "asphalt40", "asphalt40", "asphalt40", "asphalt40", "asphalt40", "asphalt40", "asphalt64", "asphalt65"],
    ["blank", "blank", "blank", "blank"],
]

track_layout = [
    {"tile": tile, "grid": [x, y], "angle": 0}
    for y, row in enumerate(tilemap)
    for x, tile in enumerate(row)
    if tile != "blank"
]

track = Track(track_layout)


class AbstractCar(pygame.sprite.Sprite):
    def __init__(self, max_velocity, rotation_velocity, start_pos):
        super().__init__()
        self.car_default = scale_image(pygame.image.load("graphics/PNG/Cars/car_black_1.png").convert_alpha(),0.4)
        self.image = self.car_default
        self.rect = self.image.get_rect(midbottom = start_pos)

        self.max_velocity = max_velocity
        self.velocity = 0
        self.rotation_velocity = rotation_velocity
        self.angle = 0
        self.acceleration = 0.1

    def rotate(self, left=False, right=False):
        if self.velocity !=0:
            rotation_amount = self.rotation_velocity * (self.velocity / self.max_velocity)
            if left:
                self.angle += rotation_amount
            if right:
                self.angle -= rotation_amount

    def draw(self, surf):
        rotated_image = pygame.transform.rotate(self.car_default, self.angle)
        new_rect = rotated_image.get_rect(center=self.rect.center)
        surf.blit(rotated_image, new_rect.topleft)

    def move_forward(self):
        self.velocity = min(self.velocity + self.acceleration, self.max_velocity)
        self.move()

    def move_backward(self):
        self.velocity = max(self.velocity - self.acceleration, -self.max_velocity/2)
        self.move()

    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.velocity
        horizontal = math.sin(radians) * self.velocity

        self.rect.x -= horizontal
        self.rect.y -= vertical

        #pygame.draw.rect(screen, (255, 0, 0), player_car.rect, 2)
        #pygame.draw.circle(screen, (0, 255, 0), player_car.rect.center, 3)

        clamp_rect = screen.get_rect().inflate(-10, -10)
        self.rect.clamp_ip(clamp_rect)


    def reduce_speed(self):
        #self.velocity = max(self.velocity - self.acceleration / 2, 0)
        self.velocity *= 0.98
        if self.velocity < 0.05:
            self.velocity = 0
        self.move()

    def update(self):
        self.move()

class PlayerCar(AbstractCar):
    def __init__(self, max_velocity, rotation_velocity, start_pos):
        super().__init__(max_velocity, rotation_velocity, start_pos)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.move_forward()
        elif keys[pygame.K_s]:
            self.move_backward()
        else:
            self.reduce_speed()

        self.rotate(left=keys[pygame.K_a], right=keys[pygame.K_d])

    def update(self):
        self.handle_input()





dirt_surface = pygame.image.load("graphics/PNG/Tiles/Dirt/land_dirt05.png").convert_alpha()

def tile_surface(surface, tile_image):
    tile_width = tile_image.get_width()
    tile_height = tile_image.get_height()
    for x in range(0, surface.get_width(), tile_width):
        for y in range(0, surface.get_height(), tile_height):
            surface.blit(tile_image, (x, y))

player_car = PlayerCar(5, 5, (100, 300))
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

            track = Track(track_layout)
    if game_active:
        tile_surface(screen, dirt_surface)
        track.draw(screen)



        player_car.update()
        player_car.draw(screen)
    else:
        screen.fill((255, 255, 255))

    clock.tick(60)
    pygame.display.update()