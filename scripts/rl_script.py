import pygame
import math
import sys
import time

import torch

sys.path.insert(0, '/Users/geraud/Documents/GitHub/platform_game')

from game_design.game_init import game_init
from reinforcement_learning.action import Action
from reinforcement_learning.state import State
from reinforcement_learning.brain import DQN, optimize_model
from reinforcement_learning.replay_memory import ReplayMemory
import torch.optim as optim

action_mapping = {0: 'left move', 1: 'right move', 2: 'spacing move'}


pygame.init()
# Game window dimensions
WIDTH, HEIGHT = 800, 600

win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple Platformer")

dqn = DQN(4, 3)
state = State()
memory = ReplayMemory(10000, action_mapping=action_mapping)
action = Action(action_mapping=action_mapping)

optimizer = optim.Adam(dqn.parameters(), lr=0.001)
num_episodes = 5800
epsilon_start = 0.62
epsilon_end = 0.1
epsilon_decay = num_episodes
epsilon_by_episode = lambda episode: epsilon_end + (epsilon_start - epsilon_end) * math.exp(-1. * episode / epsilon_decay)
batch_size = 64
action_mapping = {0: 'left move', 1: 'right move', 2: 'spacing move'}

dqn.load_state_dict(torch.load('/Users/geraud/Documents/game_weights/model_dqn_platform_game_4200.pth'))
  # Mettre le modèle en mode évaluation si vous l'utilisez pour l'inférence


for episode in range(num_episodes):
    time_start = time.time()
    if episode != 0:
        highest_reward = max(rewards)
        print(f"A l'épisode {episode - 1}, le score le plus haut était de {highest_reward.item()}")
        print(f"{(nb_know_action/nb_action) * 100:.2f}% des actions étaient basées sur la connaissance")

    epsilon = epsilon_by_episode(episode)
    player, platforms, game_rules = game_init(win)
    player_coord = (player.x, player.y)
    initial_dist = state.get_current_state(player_coord, player.platforms_coord, player.platform_num, initial_state=True)
    current_state = torch.tensor((initial_dist[0], initial_dist[1], initial_dist[2], float(player.on_platform)))

    if episode % 100 == 0 and episode != 0:
        torch.save(dqn.state_dict(), f'/Users/geraud/Documents/game_weights/model_dqn_platform_game_{episode+4200}.pth')
    rewards = []

    reward = 0
    done = False

    nb_action = 0
    nb_know_action = 0
    l_left_move_dist = []
    while not done:
        pygame.time.delay(0)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
        win.fill((0, 0, 0))

        selected_action = action.get_action(dqn, current_state, epsilon)
        player.move(selected_action.item())
        player_coord = (player.x, player.y)
        if player.score(win) > 200:
            next_state_dist = state.get_current_state(player_coord, player.platforms_coord, player.platform_num)
        else:
            next_state_dist = state.get_current_state(player_coord, player.platforms_coord, player.platform_num, initial_state=True)
        next_state = torch.tensor(
                [next_state_dist[0], next_state_dist[1], next_state_dist[2], float(player.on_platform)],
                dtype=torch.float32)

        reward = torch.tensor([player.score(win) + (1000 / next_state_dist[0])], dtype=torch.float32)
        rewards.append(reward)

        memory.push(current_state, selected_action, next_state, reward)

        current_state = next_state

        if len(memory) > batch_size:
            batch = memory.sample(batch_size)
            optimize_model(dqn, optimizer, batch)

        if game_rules.game_over:
            done = True

        win = game_rules.game_state(win, player.y, player.ground)
        platforms.move_platforms(player.platforms_coord, win)
        player.draw(win)  # Draw the player on the window
        pygame.display.update()  # Update the display

        if action.knowledge_action:
            nb_know_action += 1
        nb_action += 1

        current_time = time.time()

        if current_time - time_start > 50:
            done = True

