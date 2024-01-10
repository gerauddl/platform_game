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

dqn = DQN(2, 3)
state = State()
memory = ReplayMemory(300000, action_mapping=action_mapping)
action = Action(action_mapping=action_mapping)

optimizer = optim.Adam(dqn.parameters(), lr=0.0001)
num_episodes = 8500
epsilon_start = 0.86
epsilon_end = 0.1
epsilon_decay = num_episodes
epsilon_by_episode = lambda episode: epsilon_end + (epsilon_start - epsilon_end) * math.exp(-1. * episode / epsilon_decay)
batch_size = 1024
action_mapping = {0: 'left move', 1: 'right move', 2: 'spacing move'}

dqn.load_state_dict(torch.load('/Users/geraud/Documents/game_weights/model_dqn_platform_game_1500.pth'))
  # Mettre le modèle en mode évaluation si vous l'utilisez pour l'inférence
human_mode = False
i= 0
for episode in range(num_episodes):
    time_start = time.time()
    if episode != 0:
        highest_reward = max(rewards)
        print(f"A l'épisode {episode - 1}, le score le plus haut était de {highest_reward}")
        if nb_know_action != 0:
            for key, value in action_count.items():
                print(f"{action_mapping[key]}: {(value/nb_know_action) * 100:.2f}%")

        print(f"{(nb_know_action/nb_action) * 100:.2f}% des actions étaient basées sur la connaissance")

    action_count = {0: 0, 1: 0, 2: 0}
    epsilon = epsilon_by_episode(episode)
    if epsilon < 0.1:
        epsilon = 0.1
    player, platforms, game_rules = game_init(win)
    player_coord = (player.x, player.y)
    state.get_current_state(player_coord, player.platforms_coord, player.platform_num, win, initial_state=True)
    initial_dist = state.distances
    current_state = torch.tensor([initial_dist, float(state.direction_x)], dtype=torch.float32)

    if episode % 100 == 0 and episode != 0:
        torch.save(dqn.state_dict(), f'/Users/geraud/Documents/game_weights/model_dqn_platform_game_{episode+1500}.pth')
    rewards = []

    reward = 0
    done = False

    nb_action = 0
    nb_know_action = 0
    l_left_move_dist = []
    while not done:
        pygame.time.delay(0)
        if human_mode:
            pygame.time.delay(10)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
        win.fill((0, 0, 0))

        selected_action = action.get_action(dqn, current_state, epsilon, i, player.isJump)
        player.move(selected_action.item(), human_mode)
        if action.knowledge_action:
            action_count[selected_action.item()] +=1
        player_coord = (player.x, player.y)

        if player.score(win) > 35:
            state.get_current_state(player_coord, player.platforms_coord, player.platform_num, win)
            next_state_dist = state.distances
        else:
            state.get_current_state(player_coord, player.platforms_coord, player.platform_num, win, initial_state=True)
            next_state_dist = state.distances

        reward = player.score(win)/10 + 200/next_state_dist
        next_state = torch.tensor([next_state_dist,
                                   float(state.direction_x)], dtype=torch.float32)
        if nb_action != 0:
            reward_tens = torch.tensor([reward - old_reward], dtype=torch.float32)
            #if reward != old_reward:
                #print(f"{action_mapping[selected_action.item()]} -- reward: {reward - old_reward}")
        else:
            reward_tens = torch.tensor([reward], dtype=torch.float32)

        old_reward = reward

        rewards.append(reward)

        memory.push(current_state, selected_action, next_state, reward_tens)

        current_state = next_state

        if len(memory) > batch_size:
            batch = memory.sample(batch_size)
            optimize_model(dqn, optimizer, batch)
            #if i % 10000 == 0 and i != 0:
                #memory.get_batch_info(batch)

        if game_rules.game_over:
            done = True

        win = game_rules.game_state(win, player.y, player.ground)
        platforms.move_platforms(player.platforms_coord, win)
        state.draw_center_platform(win)
        player.draw(win)  # Draw the player on the window
        pygame.display.update()  # Update the display

        if action.knowledge_action:
            nb_know_action += 1
        nb_action += 1

        current_time = time.time()

        if player.score(win) < 100 and current_time - time_start > 10:
            done = True

        i += 1

