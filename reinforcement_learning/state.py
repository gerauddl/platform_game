from typing import List, Tuple
import pygame
class State:
    def __init__(self):
        self.next_platforms = None
        self.distances = None
        self.player_position = None
        self.platforms = None
        self.plat_num = None
        self.plat_coord = None
        self.direction_x = None
        self.direction_y = None
        self.initial_state = False

    def get_current_state(self, player_position, platforms, plat_num, win, initial_state=False):
        self.initial_state = initial_state
        self.player_position = player_position
        self.platforms = platforms
        self.plat_num = plat_num
        if not initial_state:
            self.plat_coord = self.platforms[self.plat_num]
        else:
            self.plat_coord = (0, 800, 600)
        
        self.plat_width = self.plat_coord[1] - self.plat_coord[0]
        self.get_next_platforms(initial_state)
        self.distances = [self.calculate_distance(plat) for plat in self.next_platforms[:2]]
        self.distances = [dist/10 for dist in self.distances]
        self.get_direction_x()

    def get_next_platforms(self, initial_state):
        if initial_state:
            l_plat_raw = [((platform[1] + platform[0]) / 2, platform[2]) for platform in self.platforms]
            l_plat_sorted = sorted(l_plat_raw, key=lambda x: x[1], reverse=True)
            l_plat = l_plat_sorted
        else:
            l_plat_raw = [((platform[1] + platform[0])/2, platform[2]) for platform in self.platforms if platform[2] < self.plat_coord[2]]
            l_plat_sorted = sorted(l_plat_raw, key=lambda x: x[1], reverse=True)
            l_plat = l_plat_sorted
        self.next_platforms = l_plat

    def calculate_distance(self, coord):
        x1, y1 = self.player_position
        x2, y2 = coord
        euc_dist = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

        return euc_dist

    def get_direction_x(self):

        l_x = [plat[0] for plat in self.next_platforms[:2]]

        for x in l_x:
            if self.player_position[0] < x:
                self.direction_x = 1
            else:
                self.direction_x = 0

    def get_direction_y(self):
        if self.player_position[1] > self.next_platforms[1]:
            self.direction_y = 1
        else:
            self.direction_y = 0

    def draw_center_platform(self, win):
        x, y = self.next_platforms

        pygame.draw.rect(win, (0, 255, 100), (x, y-10, 10, 10))
