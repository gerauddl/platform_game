from typing import List
import torch
import random



class Action:
    def __init__(self, action_mapping):
        self.action_mapping = action_mapping
        self.current_state = List
        self.is_on_platform = bool
        self.score = int
        self.num_actions = 3
        self.knowledge_action = False

    def get_action(self, dqn, current_state, epsilon, i, is_jump=False):

        if random.random() > epsilon:
            with torch.no_grad():
                q_values = dqn.forward(current_state)

                if i % 100 == 0:
                    print(q_values)
                action = q_values.max(0)[1].view(1, 1)
                if self.action_mapping[action.item()] == "spacing move" and is_jump:
                    _, top_indices = q_values.topk(2, dim=0)  # Récupère les indices des deux valeurs les plus élevées
                    action = top_indices[1].view(1, 1)
                #if i % 100 == 0:
                    #print(f"une action a été prise basée sur la connaissance, cette action est: {self.action_mapping[action.item()]}")
                self.knowledge_action = True
        else:
            action = torch.tensor([[random.randrange(self.num_actions)]], dtype=torch.int64)
            if self.action_mapping[action.item()] == "jumping move" and is_jump:
                action = torch.tensor([[random.randrange(2)]], dtype=torch.int64)
            self.knowledge_action = False

        return action

