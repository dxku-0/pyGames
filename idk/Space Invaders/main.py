import pygame
import os 
import time
import random
from pygame.locals import *



pygame.init()
pygame.font.init()


WIDTH, HEIGHT = 600, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("Space Invaders")


# Load images
RED_SPACE_SHIP = pygame.image.load(os.path.join("Space Invaders/assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("Space Invaders/assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("Space Invaders/assets", "pixel_ship_blue_small.png"))

# Player ship
YELLOW_SPACE_SHIP = pygame.transform.scale(pygame.image.load(os.path.join("Space Invaders/assets", "pixel_ship_yellow.png")), (50, 50))

# Lasers
RED_LASER = pygame.transform.scale(pygame.image.load(os.path.join("Space Invaders/assets", "pixel_laser_red.png")), (70, 50))
GREEN_LASER = pygame.transform.scale(pygame.image.load(os.path.join("Space Invaders/assets", "pixel_laser_green.png")), (70, 50))
BLUE_LASER = pygame.transform.scale(pygame.image.load(os.path.join("Space Invaders/assets", "pixel_laser_blue.png")), (50, 50))
YELLOW_LASER = pygame.transform.scale(pygame.image.load(os.path.join("Space Invaders/assets", "pixel_laser_yellow.png")), (50, 50))

# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("Space Invaders/assets", "background-black.png")), (WIDTH, HEIGHT))

# start images
LOAD1 = pygame.transform.scale(pygame.image.load(os.path.join("Space Invaders/assets", "load.png")), (WIDTH, HEIGHT))
LOAD2 = pygame.transform.scale(pygame.image.load(os.path.join("Space Invaders/assets", "load2.png")), (WIDTH, HEIGHT))


def collide(obj1, obj2):                          # ?
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y

    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None  


class LASER:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel
    
    def off_screen(self, height):
        on_screen = self.y <= height and self.y >= 0
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
        # pygame.draw.rect(WIN, (255, 0, 0), (self.x, self.y, 30, 30))
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)

            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)

            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = LASER(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()
    
    def get_height(self):
        return self.ship_img.get_height()

class PLAYER(SHIP):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)

            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
                
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.health_bar(window)

    def health_bar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))


class ENEMY(SHIP):
    COLOR_MAP = {
                "red" : (RED_SPACE_SHIP, RED_LASER),
                "green" : (GREEN_SPACE_SHIP, GREEN_LASER),
                "blue" :(BLUE_SPACE_SHIP, BLUE_LASER)
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

    show_health_bar = 20
    player = PLAYER(300, 550 - show_health_bar)

    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicssans", 30)
    lost_font = pygame.font.SysFont("comicssans", 60)

    enemies = []
    wave_length = 0
    enemy_vel = 2

    player_vel = 5

    laser_vel = 5
 
    lost = False
    lost_count = 0

    def redraw_window():
        WIN.blit(BG, (0, 0))

        # draw text # main.font.render(text, anti-aliasing, color)
        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))
        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))

        # window_name.blit(surface, (x, y))
        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        # get_width() method to get the width of the surface level_label

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("You Lost!", 1, (255, 255, 255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, HEIGHT/2))


        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue
        
        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = ENEMY(random.randrange(50, WIDTH-50), random.randrange(-1500, -100),
                              random.choice(["red", "green", "blue"]))
                enemies.append(enemy)   


        for event in pygame.event.get():
            if event.type == QUIT:
                run = False
        
        # pygame.key.get_pressed() returns a dictionary of all keys and whether they're pressed or not like this: {K_LEFT:True, K_RIGHT:False}
        # this method lets multiple key press work

        keys = pygame.key.get_pressed()
        if keys[K_LEFT] and player.x - player_vel > 0:
            player.x -= player_vel
        if keys[K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH:
            player.x += player_vel
        if keys[K_UP] and player.y - player_vel > 0:
            player.y -= player_vel
        if keys[K_DOWN] and player.y + player_vel + player.get_height() + show_health_bar < HEIGHT:
            player.y += player_vel
        if keys[K_SPACE]:
            player.shoot()
       
       
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 1*FPS) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 20
                enemies.remove(enemy)

            elif enemy.y + enemy.ship_img.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)
            

        player.move_lasers(-laser_vel, enemies)
        player.health_bar(WIN)


def main_menu():
    run = True

    title_font = pygame.font.SysFont("comicsans", 30)
    
    img = random.choice([LOAD1, LOAD2])

    while run:
        if img == LOAD1:
            WIN.blit(LOAD1, (0, 0))
        elif img == LOAD2:
            WIN.blit(LOAD2, (0, 0))

        title_label = title_font.render("Press the mouse to begin...", 1, (255, 255, 255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 450))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()

    pygame.quit()


main_menu()


