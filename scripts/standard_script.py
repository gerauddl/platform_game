import pygame
from game_design.player import Player
from game_design.platforms import Platforms
from game_design.game_rules import GameRules
from game_design.game_init import game_init

pygame.init()
# Game window dimensions
WIDTH, HEIGHT = 800, 600

win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple Platformer")

# Create a player instance
player = Player(x=50, y=HEIGHT - 50, width=40, height=50)
platforms = Platforms(HEIGHT, WIDTH, 300)
game_rules = GameRules()

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
    win = game_rules.game_state(win, player_y, ground)

    if game_rules.game_over and keys[pygame.K_SPACE]:
        first_round, player, platforms, game_rules = game_init()
    player.draw(win)  # Draw the player on the window
    pygame.display.update()  # Update the display

#pygame.quit()