import pygame
import math
import sys
import time
import torch
from collections import deque
import numpy as np

sys.path.insert(0, '/Users/geraud/code/game/platform_game')
print(sys.path)
from game_design.game_init import game_init
from reinforcement_learning.action import Action
from reinforcement_learning.state import State
from reinforcement_learning.brain import DQN, optimize_model
from reinforcement_learning.replay_memory import ReplayMemory
import torch.optim as optim

action_mapping = {0: 'left move', 1: 'right move', 2: 'spacing move'}

def draw_text(text, x_placement):
    pygame.font.init()  # Initialiser le module de police
    font = pygame.font.SysFont('Arial', 20)  # Choisir la police et la taille
    score_text = font.render(text, True, (0, 150, 255))
    win.blit(score_text, (x_placement, 10))

pygame.init()
# Game window dimensions
WIDTH, HEIGHT = 800, 600

win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple Platformer")

dqn = DQN(3, 3)
state = State()
memory = ReplayMemory(300000, action_mapping=action_mapping)
action = Action(action_mapping=action_mapping)

optimizer = optim.Adam(dqn.parameters(), lr=0.0001)
num_episodes = 10000
epsilon_start = 0.995
epsilon_end = 0.1
epsilon_decay = num_episodes
epsilon_by_episode = lambda episode: epsilon_end + (epsilon_start - epsilon_end) * math.exp(-1. * episode / epsilon_decay)
batch_size = 512
action_mapping = {0: 'left move', 1: 'right move', 2: 'spacing move'}

dqn.load_state_dict(torch.load('/Users/geraud/code/game/game_weights/model_dqn_platform_game_100.pth'))
  # Mettre le modèle en mode évaluation si vous l'utilisez pour l'inférence
human_mode = False
i= 0
max_scores = deque([],maxlen=30) 
highest_score = 0

for episode in range(num_episodes):
    time_start = time.time()
    if episode != 0:
        highest_ep_score = max(scores)
        max_scores.append(highest_ep_score)
        print(f"A l'épisode {100+episode - 1}, le score le plus haut était de {highest_ep_score}")
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
    current_state = torch.tensor([initial_dist, float(state.direction_x), float(player.on_platform)], dtype=torch.float32)

    if episode % 100 == 0 and episode != 0:
        torch.save(dqn.state_dict(), f'/Users/geraud/code/game/game_weights/model_dqn_platform_game_{episode+100}.pth')
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

        if player.score(win) > 35:
            state.get_current_state(player_coord, player.platforms_coord, player.platform_num, win)
            next_state_dist = state.distances
        else:
            state.get_current_state(player_coord, player.platforms_coord, player.platform_num, win, initial_state=True)
            next_state_dist = state.distances

        reward = player.score(win)/8 
        if player.score(win) > highest_score:
            highest_score = player.score(win)

        next_state = torch.tensor([next_state_dist,
                                   float(state.direction_x), float(player.on_platform),
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
        state.draw_center_platform(win)
        player.draw(win)  # Draw the player on the window

        draw_text(f"Highest score: {highest_score}", 245)
        draw_text(f"Episode: {episode+1}", 110)
        if episode == 0:
            draw_text(f"Average highest score: {0}", 450)
        else:
            draw_text(f"Average highest score: {int(np.mean(max_scores))}", 450)
        pygame.display.update()  # Update the display

        if action.knowledge_action:
            nb_know_action += 1
        nb_action += 1

        current_time = time.time()

        if player.score(win) < 100 and current_time - time_start > 7:
            done = True

        i += 1

