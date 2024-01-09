import pygame
from typing import List

class Player:
    def __init__(self, x, y, width, height, win_height, platforms_coord):
        self.x = x
        self.y = y
        self.win_height = win_height
        self.ground = win_height
        self.moving_ground = win_height
        self.width = width
        self.height = height
        self.vel = 10  # Velocity
        self.isJump = False
        self.jump_peak = False
        self.jump_vel = 10  # Vélocité initiale de saut
        self.gravity = 0.2
        self.hitbox = (self.x,  self.y, self.width, self.height)  # Used for collisions later
        self.platforms_coord = List
        self.on_platform = False
        self.platform_num = int
        self.platforms_coord = platforms_coord
        self.bin_platform = 1
        self.plat_coord = (0, win_height, 0)

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

    def move(self, action_num=None, human_mode=False):
        keys = pygame.key.get_pressed()

        self.is_on_platform()

        # left move
        if not human_mode:
            if action_num == 0 and self.x > self.vel:
                self.x -= self.vel
            if action_num == 1 and self.x < 800 - self.width - self.vel:
                self.x += self.vel
        else:
            if keys[pygame.K_LEFT] and self.x > self.vel:
                self.x -= self.vel
            if keys[pygame.K_RIGHT] and self.x < 800 - self.width - self.vel:
                self.x += self.vel

        # right move


        if not self.isJump:
            # jumping move
            if not human_mode:
                if action_num == 2:
                    self.isJump = True
                    if self.on_platform:
                        self.on_platform = False
                    #self.y += 7
                    self.jump_move()
            else:
                if keys[pygame.K_SPACE]:
                    self.isJump = True
                    if self.on_platform:
                        self.on_platform = False
                        # self.y += 7
                    self.jump_move()


                else:
                    if self.on_platform:
                        x1, x2, y = self.platforms_coord[self.platform_num]
                        self.y = y - self.height
                    elif self.moving_ground == 600:
                        self.y = self.ground - self.height
        else:
            self.jump_move()

        if self.y < self.win_height/2:
            self.y = self.win_height/2
            self.moving_ground += self.jump_vel
            self.move_window()

        return self.ground, self.is_on_platform(), self.plat_coord

    def is_on_platform(self):
        for i, (x1, x2, y) in enumerate(self.platforms_coord):
            if (y < self.y + self.height < y + 12) and (x1 < self.x + self.width and x2 > self.x):
                self.y = y - self.height
                self.on_platform = True
                self.platform_num = i
                self.jump_peak = False
                self.isJump = False
                self.jump_vel = 10
                self.bin_platform = 1
                self.plat_coord = self.platforms_coord[i]
                return True
        if self.on_platform:
            x1, x2, y = self.platforms_coord[self.platform_num]
            if not (x1 < self.x + self.width and x2 > self.x):
                self.isJump = True
                self.jump_peak = True
                self.jump_vel = 0
                self.jump_move()
                self.on_platform = False
                self.bin_platform = 0
                return False
        self.bin_platform = 0
        return False

    def move_window(self):
        platforms_y = [platform_coord[2] for platform_coord in self.platforms_coord]
        for i, y in enumerate(platforms_y):
            self.platforms_coord[i] = self.platforms_coord[i][:2] + (y + self.jump_vel,)

    def score(self, win):

        pygame.font.init()  # Initialiser le module de police
        font = pygame.font.SysFont('Arial', 20)  # Choisir la police et la taille
        score = int(self.moving_ground - 600)
        score_text = font.render(f"Score:{score}", True, (0, 100, 255))
        win.blit(score_text, (10, 10))

        return score
