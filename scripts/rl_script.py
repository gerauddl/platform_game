import os

import pygame
import math
import sys
import time
import torch
from collections import deque
import numpy as np
import random

import multiprocessing
from functools import partial

sys.path.insert(0, '/Users/geraud/Documents/GitHub/platform_game')

from game_design.game_init import game_init
from reinforcement_learning.action import Action
from reinforcement_learning.state import State
from reinforcement_learning.brain import DQN, optimize_model
from reinforcement_learning.replay_memory import ReplayMemory
import torch.optim as optim


def draw_text(text, x_placement, win):
    pygame.font.init()  # Initialiser le module de police
    font = pygame.font.SysFont('Arial', 20)  # Choisir la police et la taille
    score_text = font.render(text, True, (0, 150, 255))
    win.blit(score_text, (x_placement, 10))


def rl_training(index, num_episodes, dqn_input, batch_size, epsilon_start, memory_len, human_mode = False, weights_num = None, load_weights=False):

    os.mkdir(f'/Users/geraud/Documents/game_weights/pool_{index}')
    pygame.init()
    # Game window dimensions
    WIDTH, HEIGHT = 800, 600
    human_mode = human_mode
    i = 0
    max_scores = deque([], maxlen=30)
    highest_score = 0
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Simple Platformer")
    epsilon_end = 0.1
    epsilon_decay = num_episodes
    epsilon_by_episode = lambda episode: epsilon_end + (epsilon_start - epsilon_end) * math.exp(
        -1. * episode / epsilon_decay)
    action_mapping = {0: 'left move', 1: 'right move', 2: 'spacing move'}

    dqn = DQN(dqn_input, 3)

    if load_weights:
        dqn.load_state_dict(torch.load(f'/Users/geraud/Documents/game_weights/pool_{index}/model_dqn_platform_game_{weights_num}.pth'))

    state = State()
    memory = ReplayMemory(memory_len, action_mapping=action_mapping)
    action = Action(action_mapping=action_mapping)
    optimizer = optim.Adam(dqn.parameters(), lr=0.001)

    for episode in range(num_episodes):
        time_start = time.time()
        if episode != 0:
            highest_ep_score = max(scores)
            max_scores.append(highest_ep_score)
            print(f"A l'épisode {episode - 1}, le score le plus haut était de {highest_ep_score}")
            if nb_know_action != 0:
                for key, value in action_count.items():
                    print(f"{action_mapping[key]}: {(value/nb_know_action) * 100:.2f}%")

            print(f"{(nb_know_action/nb_action) * 100:.2f}% des actions étaient basées sur la connaissance")

        action_count = {0: 0, 1: 0, 2: 0}
        epsilon = epsilon_by_episode(episode)
        if epsilon < 0.1:
            epsilon = 0.1
        print(epsilon)
        player, platforms, game_rules = game_init(win)
        player_coord = (player.x, player.y)
        state.get_current_state(player_coord, player.platforms_coord, player.platform_num, win, initial_state=True)
        initial_dist = state.distances
        current_state = torch.tensor([initial_dist[0], float(state.direction_x),
                                      ], dtype=torch.float32)

        if episode % 100 == 0 and episode != 0:
            torch.save(dqn.state_dict(), f'/Users/geraud/Documents/game_weights/pool_{index}/model_dqn_platform_game_{episode}.pth')
        scores = []

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

            if player.score(win) > 280:
                state.get_current_state(player_coord, player.platforms_coord, player.platform_num, win)
                next_state_dist = state.distances
            else:
                state.get_current_state(player_coord, player.platforms_coord, player.platform_num, win, initial_state=True)
                next_state_dist = state.distances

            reward = player.score(win)/10 + 1000/next_state_dist[0]
            if player.score(win) > highest_score:
                highest_score = player.score(win)

            next_state = torch.tensor([next_state_dist[0],
                                       float(state.direction_x)
                                       ], dtype=torch.float32)
            if nb_action != 0:
                reward_tens = torch.tensor([reward - old_reward], dtype=torch.float32)
                #if reward != old_reward:
                    #print(f"{action_mapping[selected_action.item()]} -- reward: {reward - old_reward}")
            else:
                reward_tens = torch.tensor([reward], dtype=torch.float32)

            old_reward = reward

            scores.append(player.score(win))

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
            player.draw(win)  # Draw the player on the window

            draw_text(f"Highest score: {highest_score}", 300, win)
            draw_text(f"Episode: {episode+1}/{num_episodes}", 110, win)
            if episode == 0:
                draw_text(f"Average highest score: {0}", 505, win)
            else:
                draw_text(f"Average highest score: {int(np.mean(max_scores))}", 505, win)
            pygame.display.update()  # Update the display

            if action.knowledge_action:
                nb_know_action += 1
            nb_action += 1

            current_time = time.time()

            if player.score(win) < 100 and current_time - time_start > 7:
                done = True
            if current_time - time_start > 70:
                done = True

            i += 1

10000*2**12
if __name__ == "__main__":
    #num_episodes, dqn_input, batch_size, epsilon_start, memory_len

    t_id = [i+1 for i in range(12)]
    l_batch_size = [64 * 2 ** (i // 2) for i in range(14)]
    l_memory_len = [10000 * 2 ** (i // 2) for i in range(14)]
    random.shuffle(l_batch_size)
    random.shuffle(l_memory_len)
    input = [(id, 2000, 2, batch_size, 1, mem) for id, batch_size, mem in zip(t_id, l_batch_size, l_memory_len)]
    print(input)
    rl_train_mp = partial(rl_training)
    num_process = 12
    pool = multiprocessing.Pool(num_process)
    result = pool.starmap(rl_train_mp, input)
