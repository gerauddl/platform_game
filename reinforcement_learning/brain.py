import torch
import torch.nn as nn


class DQN(nn.Module):
    def __init__(self, num_inputs, num_actions):
        super(DQN, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(num_inputs, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, num_actions)
        )

    def forward(self, x):
        return self.net(x)


def optimize_model(dqn, optimizer, batch, gamma=0.99):

    l_states = [trans.state for trans in batch]
    l_actions = [trans.action for trans in batch]
    l_next_states = [trans.next_state for trans in batch]
    l_rewards = [trans.reward for trans in batch]

    states = torch.stack(l_states)
    actions = torch.stack(l_actions)
    next_states = torch.stack(l_next_states)
    rewards = torch.stack(l_rewards).squeeze(-1)


    # Obtenir les Q-values actuelles
    state_action_values = dqn.forward(states).gather(1, actions.squeeze(-1)).squeeze(-1)

    # Calculer les Q-values cibles
    next_state_values = dqn.forward(next_states).max(1)[0].detach()
    expected_state_action_values = rewards + (gamma * next_state_values)
    expected_state_action_values = expected_state_action_values.squeeze(-1)


    # Calculer la perte
    loss = nn.MSELoss()(state_action_values, expected_state_action_values)
    # Optimisation
    optimizer.zero_grad()
    loss.backward()
    torch.nn.utils.clip_grad_norm_(dqn.parameters(), 5)
    optimizer.step()
