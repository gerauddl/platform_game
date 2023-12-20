import pygame
import random
from typing import List

class Player:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.ground = 600
        self.moving_ground = 600
        self.width = width
        self.height = height
        self.vel = 10  # Velocity
        self.isJump = False
        self.jump_peak = False
        self.jump_vel = 10  # Vélocité initiale de saut
        self.gravity = 0.2
        self.jump_y_coordinate = None
        self.jumpCount = 0
        self.hitbox = (self.x,  self.y, self.width, self.height)  # Used for collisions later
        self.platforms_coord = List
        self.on_platform = False
        self.platform_num = int
        self.platforms_coord = []

    def draw(self, win):
        pygame.draw.rect(win, (255, 0, 0), (self.x, self.y, self.width, self.height))

    def jump_move(self):
        if self.jump_peak:
            # Descendre
            if self.y + self.height < self.moving_ground:

                self.y += self.jump_vel
                self.jump_vel += self.gravity
            else:
                self.isJump = False
                self.jump_peak = False
                self.jump_vel = 10

        else:
            # Monter
            self.y -= self.jump_vel
            self.jump_vel -= self.gravity

            if self.jump_vel <= 0:
                self.jump_peak = True

    def move(self, platforms_coord, win_height):
        self.platforms_coord = platforms_coord
        keys = pygame.key.get_pressed()
        self.is_on_platform()
        if keys[pygame.K_LEFT] and self.x > self.vel:
            self.x -= self.vel

        if keys[pygame.K_RIGHT] and self.x < 800 - self.width - self.vel:
            self.x += self.vel

        if not self.isJump:
            if keys[pygame.K_SPACE]:
                self.isJump = True
                if self.on_platform:
                    self.on_platform = False
                    #self.y += 7
                self.jump_move()

            else:
                if self.on_platform:
                    x1, x2, y = self.platforms_coord[self.platform_num]
                    self.y = y - self.height
                elif self.moving_ground == 600:
                    self.y = self.ground - self.height
        else:
            self.jump_move()



        if self.y < win_height/2:
            self.y = win_height/2
            self.moving_ground += self.jump_vel
            self.move_window()

        return self.platforms_coord, self.y, self.ground

    def is_on_platform(self):
        for i, (x1, x2, y) in enumerate(self.platforms_coord):
            if (y < self.y + self.height < y + 12) and (x1 < self.x + self.width and x2 > self.x):
                self.y = y - self.height
                self.on_platform = True
                self.platform_num = i
                self.jump_peak = False
                self.isJump = False
                self.jump_vel = 10
                return True
        if self.on_platform:
            x1, x2, y = self.platforms_coord[self.platform_num]
            if not (x1 < self.x + self.width and x2 > self.x):
                self.isJump = True
                self.jump_peak = True
                self.jump_vel = 0
                self.jump_move()
                self.on_platform = False
                return False
        return False

    def move_window(self):
        platforms_y = [platform_coord[2] for platform_coord in self.platforms_coord]
        for i, y in enumerate(platforms_y):
            self.platforms_coord[i] = self.platforms_coord[i][:2] + (y + self.jump_vel,)

    def score(self, win):
        pygame.font.init()  # Initialiser le module de police
        font = pygame.font.SysFont('Arial', 20)  # Choisir la police et la taille
        score_text = font.render(f"Score:{int(self.moving_ground - 600)}", True, (0, 100, 255))
        win.blit(score_text, (10, 10))




class Platforms:
    def __init__(self, win_height, win_width, number_platforms):
        self.height = 5
        self.width = []
        self.number_platforms = number_platforms
        self.win_height = win_height
        self.win_width = win_width
        self.seed = 2

    def set_platform_position(self, i):
        width = random.randint(40, 150)
        x = random.randint(0, self.win_width - width)
        y = random.randint(self.win_height - 230 - (130*i), (self.win_height - 100) - (130*i))
        return x, y, width

    def draw_platform(self, x, y, width, win):
        pygame.draw.rect(win, (255, 0, 0), (x, y, width, self.height))
    def draw_center_platform(self, win, x, y):
        pygame.draw.rect(win, (0, 255, 0), (x, y, 5, 5))

    def set_platforms(self, win):
        platforms_coordinates = []
        for i in range(self.number_platforms):
            random.seed(self.seed + i)
            x, y, width = self.set_platform_position(i)
            self.width.append(width)
            platforms_coordinates.append((x, x + self.width[i], y))
            self.draw_platform(x, y, self.width[i], win)
            self.draw_center_platform(win, x, y)
            self.draw_center_platform(win, x + self.width[i], y)

        return platforms_coordinates

    def move_platforms(self, platforms_coordinates, win):
        for i, (x1, x2, y) in enumerate(platforms_coordinates):
            pygame.draw.rect(win, (255, 0, 0), (x1, y, self.width[i], self.height))


class GameRules:
    def __init__(self):
        self.player_y = 1
        self.ground = 0
        self.game_over = False

    def game_state(self, win, player_y, ground):
        self.player_y = player_y
        self.ground = ground
        if self.is_loosing():
            pygame.font.init()  # Initialiser le module de police
            font = pygame.font.SysFont('Arial', 50)  # Choisir la police et la taille
            game_over_text = font.render('Game Over', True, (255, 0, 0))
            win.fill((0, 0, 0))
            win.blit(game_over_text, (200, 300))
            self.game_over = True
            return win
        return win

    def is_loosing(self):
        if self.player_y > self.ground + 10:
            return True
        return False


def game_init():
    WIDTH, HEIGHT = 800, 600
    player = Player(x=50, y=HEIGHT - 50, width=40, height=50)
    platforms = Platforms(HEIGHT, WIDTH, 300)
    gamerules = GameRules()
    first_round = True
    return first_round, player, platforms, gamerules

pygame.init()
# Game window dimensions
WIDTH, HEIGHT = 800, 600

win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple Platformer")

# Create a player instance
player = Player(x=50, y=HEIGHT - 50 , width=40, height=50)
platforms = Platforms(HEIGHT, WIDTH, 300)
gamerules = GameRules()

# Main game loop
running = True
first_round = True
while running:

    pygame.time.delay(10)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    win.fill((0, 0, 0))  # Fill the screen with black
    if first_round:
        platforms_coordinates = platforms.set_platforms(win)
        first_round = False
    keys = pygame.key.get_pressed()

    platforms_coordinates, player_y, ground = player.move(platforms_coordinates, HEIGHT)  # Move the player based on key inputs
    platforms.move_platforms(platforms_coordinates, win)
    player.score(win)
    win = gamerules.game_state(win, player_y, ground)

    if gamerules.game_over and keys[pygame.K_SPACE]:
        first_round, player, platforms, gamerules = game_init()
    player.draw(win)  # Draw the player on the window
    pygame.display.update()  # Update the display

#pygame.quit()

#enregistrer le temps de parcours