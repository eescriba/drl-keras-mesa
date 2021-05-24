from mesa import Model
from mesa.time import BaseScheduler

from .rl import RLlibAgent


class RLlibActivation(BaseScheduler):
    """
    RLlib agent scheduler
    """

    def __init__(self, model: Model, rl_agent: RLlibAgent) -> None:
        super().__init__(model)
        self.rl_agent = rl_agent
        self.reward = 0
        self.last_reward = 0

    def next_action(self):
        return self.rl_agent.agent.compute_action(self.model.env.s)

    def forward(self, action):
        """
        Execute next action
        """
        state, reward, done, info = self.model.env.step(action)
        print(state, reward, done, info)
        self.last_reward = reward
        self.reward += reward

        return done

    def step(self) -> None:
        """
        Executes the step of all agents, one at a time, in random order.
        """
        action = self.next_action()
        self.forward(action)

        for agent in self.agent_buffer(shuffled=True):
            agent.step()

        self.steps += 1
        self.time += 1


class RLKerasActivation(BaseScheduler):
    """
    Keras-RL agent scheduler
    """

    def __init__(self, model, rl_agent) -> None:
        super().__init__(model)
        self.rl_agent = rl_agent
        self.reward = 0

    def forward(self):
        """
        Execute next action
        """
        action = self.rl_agent.forward(self.model.env.s)
        observation, reward, done, info = self.model.env.step(action)
        print(observation, reward, done, info)
        self.model.env.s = observation
        self.reward += reward
        if done:
            self.rl_agent.forward(observation)
            self.rl_agent.backward(0.0, terminal=False)
        return done

    def step(self) -> None:
        """
        Executes the step of all agents, one at a time, in random order.
        """
        self.forward()

        for agent in self.agent_buffer(shuffled=True):
            agent.step()

        self.steps += 1
        self.time += 1
