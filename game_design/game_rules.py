import pygame

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
