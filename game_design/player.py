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
        self.vel = 15  # Velocity
        self.going_right = False
        self.going_left = False
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
        self.is_falling = False

    def draw(self, win):
        pygame.draw.rect(win, (255, 0, 0), (self.x, self.y, self.width, self.height))

    def jump_move(self):
        if self.jump_peak:
            # Descendre
            if self.y + self.height < self.moving_ground:
                if not self.is_falling:
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
                self.going_right = False
                self.going_left = True
                self.vel_fading = 10
            if action_num == 1 and self.x < 800 - self.width - self.vel:
                self.x += self.vel
                self.going_right = True
                self.going_left = False
                self.vel_fading = 10
        else:
            if keys[pygame.K_LEFT] and self.x > self.vel:
                self.x -= self.vel
                self.going_right = False
                self.going_left = True
                self.vel_fading = 10
            if keys[pygame.K_RIGHT] and self.x < 800 - self.width - self.vel:
                self.x += self.vel
                self.going_right = True
                self.going_left = False
                self.vel_fading = 10

        #if self.going_right and self.x < self.vel_fading:
            #self.x += self.vel_fading
            #if self.vel_fading >= 1:
                #self.vel_fading -= 1

        #if self.going_left and self.x > self.vel_fading:
            #self.x -= self.vel_fading
            #if self.vel_fading >= 1:
                #self.vel_fading -= 1
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

        if self.y + self.height < self.win_height/2:
            self.y = self.win_height/2 - self.height
            self.moving_ground += self.jump_vel
            self.move_window()

        if self.y + self.height >= self.win_height and self.moving_ground != self.win_height:
            self.y = self.win_height - self.height
            self.moving_ground -= self.jump_vel
            self.move_window(up=False)
            self.is_falling = True
            if 590 < self.moving_ground < 610:
                self.moving_ground = 600
                self.isJump = False
                self.is_falling = False

        if self.moving_ground - 1 < self.y + self.height < self.moving_ground + 1:
            if not human_mode:
                self.platform_num = None
                self.on_platform = True
            else:
                pass
        else:
            if not human_mode:
                self.on_platform = False

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
                self.is_falling =False
                return True
            
        if self.on_platform:
            if self.moving_ground - 1 < self.y + self.height < self.moving_ground + 1:
                x1, x2, y = (0, 800, 600)
            else:
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

    def move_window(self, up=True):
        platforms_y = [platform_coord[2] for platform_coord in self.platforms_coord]
        if up:
            for i, y in enumerate(platforms_y):
                self.platforms_coord[i] = self.platforms_coord[i][:2] + (y + self.jump_vel,)
        else:
            for i, y in enumerate(platforms_y):
                self.platforms_coord[i] = self.platforms_coord[i][:2] + (y - self.jump_vel,)

    def score(self):
        player_height = self.moving_ground - 600
        return int(player_height)
