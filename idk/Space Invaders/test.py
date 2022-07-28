import os
import random
import pygame
from pygame.locals import *





pygame.init()

WIDTH, HEIGHT = 600, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))



# LOADING IMAGES
# background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (HEIGHT, WIDTH))

RED_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

# Player ship
YELLOW_SHIP = pygame.transform.scale(pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png")), (50, 50))

# Lasers
RED_LASER = pygame.transform.scale(pygame.image.load(os.path.join("assets", "pixel_laser_red.png")), (70, 50))
GREEN_LASER = pygame.transform.scale(pygame.image.load(os.path.join("assets", "pixel_laser_green.png")), (70, 50))
BLUE_LASER = pygame.transform.scale(pygame.image.load(os.path.join("assets", "pixel_laser_blue.png")), (50, 50))
YELLOW_LASER = pygame.transform.scale(pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png")), (50, 50))


def collide(obj1, obj2):
    offset_x = obj2.x = obj1.x
    offset_y = obj2.y = obj1.y

    return obj1.mask.overlap(obj2, offset_x, offset_y) != None


class LASER:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))
    
    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        on_screen = 0 <= self.y < HEIGHT
        return not(on_screen)

    def collision(self, obj):
        return collide(obj, self)



class SHIP:
    COOLDOWN = 30
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health

        self.ship_img = None
        self.laser_img = None
        self.lasers = []

        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_laser(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)

            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)


    def shoot(self):
        if self.cool_down_counter == 0:
            laser = LASER(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
    
    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1


class PLAYER(SHIP):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)

    def draw(self, window):
        super().draw(window)

    def move_laser(self, vel, objs):
        super().move_laser(vel)

        for laser in self.lasers:
            laser.move(vel)

            if laser.off_screen:
                self.lasers.remove(laser)

            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.lasers.remove(laser)


    

class ENEMY(SHIP):
    COLOR_MAP = {
                "red" : (RED_SHIP, RED_LASER), 
                "green" : (GREEN_SHIP, GREEN_LASER), 
                "blue" : (BLUE_SHIP, BLUE_LASER)
                }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    




def main():
    run = True
    FPS = 60
    clock = pygame.time.Clock()

    level = 0
    wavelength = 0

    player = PLAYER(300, (600 - YELLOW_SHIP.get_height() - 10))

    player_vel = 5
    enemy_vel = 2
    laser_vel = 4

    enemies = []
    if len(enemies) == 0:
        level += 1
        wavelength += 5
        for i in range(wavelength):
            enemy = ENEMY(random.randrange(30, WIDTH - 60), random.randrange(-1500, -50), 
                    random.choice(["red", "green", "blue"]))
            enemies.append(enemy)



    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == QUIT:
                run = False
        
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                run = False
        
        keys = pygame.key.get_pressed()
        if keys[K_UP]:
            player.y -= player_vel
        if keys[K_DOWN]:
            player.y += player_vel
        if keys[K_RIGHT]:
            player.x += player_vel
        if keys[K_LEFT]:
            player.x -= player_vel
        if keys[K_SPACE]:
            player.shoot()
        

        WIN.blit(BG, (0, 0))
        player.draw(WIN)
        for enemy in enemies:
            enemy.draw(WIN)
            enemy.move(enemy_vel)
            enemy.move_laser(laser_vel)

            if random.randrange(0, 1*FPS) == 1:
                enemy.shoot()

            if enemy.y + enemy.ship_img.get_height() > HEIGHT:
                enemies.remove(enemy)
        
        player.move_laser(-laser_vel)

        
        pygame.display.update()



main()
