from game_design.player import Player
from game_design.platforms import Platforms
from game_design.game_rules import GameRules

import random


def game_init(win):

    width, height = 800, 600
    platforms = Platforms(height, width, 300)
    platforms_coordinates = platforms.set_platforms(win)
    player = Player(x=400, y=600,
                    width=40,
                    height=50,
                    win_height=height,
                    platforms_coord=platforms_coordinates)
    game_rules = GameRules()

    return player, platforms, game_rules
