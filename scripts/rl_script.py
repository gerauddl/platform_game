import json
import os
import pygame
import math
import sys
import time
from collections import deque
import numpy as np
import random
from multiprocessing import Process, Queue
import matplotlib.pyplot as plt

sys.path.insert(0, '/Users/geraud/Documents/GitHub/platform_game')

from game_design.game_init import game_init
from reinforcement_learning.action import Action
from reinforcement_learning.state import State
from reinforcement_learning.brain import *
from reinforcement_learning.replay_memory import ReplayMemory
import torch.optim as optim


def draw_text(text, x, y, win):
    pygame.font.init()  # Initialiser le module de police
    font = pygame.font.SysFont('Arial', 20)  # Choisir la police et la taille
    score_text = font.render(text, True, (0, 150, 255))
    win.blit(score_text, (x, y))

n=1
fig, ax = plt.subplots()
lines = []  # Pour stocker les objets de ligne
pool_names = [f"Process {i+1}" for i in range(n)]  # Exemple de noms de process

for name in pool_names:
    line, = ax.plot([], [], label=name)
    lines.append(line)

ax.set_xlabel('Épisodes')
ax.set_ylabel('Score')
ax.set_title('Progression du Score par Épisode')
ax.legend()


def update_graph(data_by_pool):
    """
    Mise à jour du graphique avec de nouvelles données pour chaque pool.

    :param data_by_pool: Liste de tuples, chaque tuple contient deux listes (new_data_y1, new_data_y2) pour un pool.
    """
    for line, new_data_y1 in zip(lines, data_by_pool):
        new_data_x = range(new_data_y1.shape)  # Supposons que x est toujours une séquence de 0 à len(new_data_y1)-1
        line.set_data(new_data_x, new_data_y1)  # Mise à jour avec new_data_y1 pour simplification

    ax.set_title(f"Progression du Score par Episode pour l'entrainement")

    ax.relim()
    ax.autoscale_view()
    plt.draw()
    plt.pause(0.01)

def rl_training(index,
                num_episodes,
                dqn_input,
                batch_size,
                epsilon_start,
                memory_len,
                lr, queue,
                human_mode=False,
                weights_num=0,
                load_weights=False):
    weights_path = f'/Users/geraud/Documents/game_weights/pool_{index}'
    pool_info = {'batch_size': batch_size,
                 'memory_len': memory_len,
                 'lr': lr
                 }
    with open(f'{weights_path}/pool_metadata.json', 'w') as f:
        json.dump(pool_info, f)
    if not os.path.exists(weights_path):
        os.mkdir(weights_path)
    pygame.init()
    # Game window dimensions
    WIDTH, HEIGHT = 800, 600
    human_mode = human_mode
    i = 0
    l_scores = []
    max_scores = deque([], maxlen=30)
    moving_average = []
    highest_score_all_time = 0
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Simple Platformer")
    epsilon_end = 0.1
    epsilon_decay = num_episodes/2
    epsilon_by_episode = lambda episode: epsilon_end + (epsilon_start - epsilon_end) * math.exp(-1. * episode / epsilon_decay)
    action_mapping = {0: 'left move', 1: 'right move', 2: 'spacing move', 3: 'no move'}

    dqn = DQN(dqn_input, 4)

    if load_weights:
        dqn.load_state_dict(torch.load(f'/Users/geraud/Documents/game_weights/pool_{index}/model_dqn_platform_game_{weights_num}.pth'))

    state = State()
    memory = ReplayMemory(memory_len, action_mapping=action_mapping)
    action = Action(action_mapping=action_mapping)
    optimizer = optim.Adam(dqn.parameters(), lr=lr)

    for episode in range(num_episodes):
        time_start = time.time()
        if episode != 0:
            highest_ep_score = highest_score
            #l_scores.append(highest_ep_score)
            max_scores.append(highest_ep_score)
            moving_average.append(np.mean(max_scores))
            queue.put((index, episode, np.mean(max_scores)))
            time.sleep(0.1)

            print(f"A l'épisode {weights_num + episode - 1}, le score le plus haut était de {highest_ep_score}")
            if nb_know_action != 0:
                for key, value in action_count.items():
                    print(f"{action_mapping[key]}: {(value/nb_know_action) * 100:.2f}%")

            print(f"{(nb_know_action/nb_action) * 100:.2f}% des actions étaient basées sur la connaissance")

        action_count = {0: 0, 1: 0, 2: 0, 3: 0}
        epsilon = epsilon_by_episode(episode)
        if epsilon < 0.1:
            epsilon = 0.1
        print(epsilon)
        player, platforms, game_rules = game_init(win)
        player_coord = (player.x, player.y)
        state.get_current_state(player_coord, player.platforms_coord, player.platform_num, win, initial_state=True)
        initial_dist = state.distances

        current_state = torch.tensor([1, state.direction_x, player.isJump, 1], dtype=torch.float32)

        if episode % 100 == 0 and episode != 0:
            torch.save(dqn.state_dict(), f'/Users/geraud/Documents/game_weights/pool_{index}/model_dqn_platform_game_{weights_num + episode}.pth')
        scores = []

        done = False
        highest_score = 0
        nb_action = 0
        nb_know_action = 0
        l_next_state = []
        l_jump_vel = []
        l_reward = []
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

            if type(player.platform_num) == int:
                state.get_current_state(player_coord, player.platforms_coord, player.platform_num, win)
                next_state_dist = state.distances
            else:
                state.get_current_state(player_coord, player.platforms_coord, player.platform_num, win, initial_state=True)
                next_state_dist = state.distances

            reward = player.score() - next_state_dist[0]*1.25

            if player.score() > highest_score:
                highest_score = player.score()
            if player.score() > highest_score_all_time:
                highest_score_all_time = player.score()

            l_next_state.append(next_state_dist[0])
            l_jump_vel.append(player.jump_vel)

            if (np.min(l_next_state) != np.max(l_next_state)) and (np.min(l_jump_vel) != np.max(l_jump_vel)):
                next_state_dist_standard = (next_state_dist[0] - np.min(l_next_state))/(np.max(l_next_state) - np.min(l_next_state))
                jump_vel_standard = (player.jump_vel - np.min(l_jump_vel))/(np.max(l_jump_vel) - np.min(l_jump_vel))
            else:
                next_state_dist_standard = 0.8
                jump_vel_standard = 0.8
            next_state = torch.tensor([next_state_dist_standard, state.direction_x, player.isJump, jump_vel_standard
                                       ], dtype=torch.float32)

            if nb_action != 0:
                reward_tens = torch.tensor([reward - old_reward], dtype=torch.float32)
                #if i % 10 ==0:
                    #keys = pygame.key.get_pressed()
                    #pygame.K_RIGHT
                    #print(f"""L'agent s'est déplacé à {"droite" if keys[pygame.K_RIGHT] else "gauche"}
                     #alors qu'il devait allé à {action_mapping[state.direction_x]}
                     #Et pour avoir effectué cette action voici son reward: {reward_tens.item()}""")
                #if reward != old_reward:
                    #print(f"{action_mapping[selected_action.item()]} -- reward: {reward - old_reward}")
            else:
                reward_tens = torch.tensor([reward], dtype=torch.float32)

            old_reward = reward

            scores.append(player.score())

            memory.push(current_state, selected_action, next_state, reward_tens)

            current_state = next_state

            if len(memory) > batch_size:
                batch = memory.sample(batch_size)
                optimize_model(dqn, optimizer, batch, i)

                if i % 500 == 0 and i != batch_size - 1:
                    update_target_network(dqn)
                if i % 500 == 0 and i != 0:
                    memory.get_batch_info(batch)

            if game_rules.game_over:
                done = True

            win = game_rules.game_state(win, player.y, player.ground)
            platforms.move_platforms(player.platforms_coord, win)
            player.draw(win)  # Draw the player on the window

            draw_text(f"Highest score: {highest_score}", 300, 10, win)
            draw_text(f"ID: {index}", 10, 30, win)
            draw_text(f"Score: {int(reward)}", 10, 10, win)
            draw_text(f"Episode: {weights_num+episode+1}/{weights_num + num_episodes}", 110, 10, win)
            if episode == 0:
                draw_text(f"Average highest score: {0}", 505, 10, win)
            else:
                draw_text(f"Average highest score: {int(np.mean(max_scores))}", 505, 10, win)
            pygame.display.update()  # Update the display

            if action.knowledge_action:
                nb_know_action += 1
            nb_action += 1

            current_time = time.time()

            if player.score() < 375 and current_time - time_start > 7:
                done = True
            if player.score() < 3000 and current_time - time_start > 25:
                done = True
            elif current_time - time_start > 110:
                done= True

            if reward < -110:
                done = True
            #if i != 0 and i % 3000 == 0:
                #epsilon = epsilon_by_episode(episode)
                #episode += 1

            i += 1

if __name__ == "__main__":

    plt.ion()
    fig, ax = plt.subplots()
    ax.set_xlabel('Épisodes')
    ax.set_ylabel('Score')
    ax.set_title('Progression du Score par Épisode')

    n = 12  # Nombre de pools
    num_episodes = 400
    queue = Queue()
    lines = {}
    data = {i: ([], []) for i in range(1, n + 1)}

    for i in range(1, n+1):
        line, = ax.plot([], [], label=f'Pool {i}')
        lines[i] = line
    ax.legend()

    l_id = [i+1 for i in range(n)]
    l_batch_size = [int(16 * 1.5 ** (i // 2)) for i in range(n+2)]
    l_memory_len = [int(2500 * 1.5 ** (i // 2)) for i in range(n+2)]
    l_lr = [0.00000001*1.5**i for i in range(1, n+1)]
    random.shuffle(l_batch_size)
    random.shuffle(l_memory_len)
    random.shuffle(l_lr)

    #input = [(id, 2000, 4, batch_size, 1, mem, lr) for id, batch_size, mem, lr in zip(l_id, l_batch_size, l_memory_len, l_lr)]

    # processes = [Process(target=rl_training, args=(id, num_episodes, 4, batch_size, 1, mem, lr, queue)) for id, batch_size, mem, lr in zip(l_id, l_batch_size, l_memory_len, l_lr)]
    processes = [Process(target=rl_training, args=(1, num_episodes, 4, 24, 1, 18984, 1.5*(10**-8), queue))]

    for p in processes:
        p.start()

    #input = [(1, 2000, 4, 64, 1, 60000, 0.00001)]
    try:
        while any(p.is_alive() for p in processes) or not queue.empty():
            while not queue.empty():
                pool_id, episode, score = queue.get()
                x_data, y_data = data[pool_id]
                x_data.append(episode)
                y_data.append(score)
                lines[pool_id].set_data(x_data, y_data)

            ax.relim()
            ax.autoscale_view(True, True, True)
            fig.canvas.draw()
            fig.canvas.flush_events()
            time.sleep(0.01)
    finally:
        for p in processes:
            p.join()
        queue.close()

    plt.ioff()
    plt.show()
