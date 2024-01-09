from collections import namedtuple, deque
import random
from collections import defaultdict

Transition = namedtuple('Transition', ('state', 'action', 'next_state', 'reward'))

reward_sums = defaultdict(float)
counts = defaultdict(int)


class ReplayMemory(object):

    def __init__(self, capacity, action_mapping):
        self.memory = deque([],maxlen=capacity)
        self.action_mapping = action_mapping

    def push(self, *args):
        self.memory.append(Transition(*args))

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)

    def get_batch_info(self, batch):

        for transition in batch:
            action = transition.action.item()
            reward = transition.reward.item()
            reward_sums[action] += reward
            counts[action] += 1

        average_rewards = {self.action_mapping[action]: reward_sums[action] / counts[action] for action in reward_sums}

        print(average_rewards)

    def __len__(self):
        return len(self.memory)


