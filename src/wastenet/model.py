import math
from enum import Enum

from mesa import Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from mesa.space import NetworkGrid

from core.rl import PPOAgent
from .agents import DumpsterAgent, BaseAgent
from .enums import WasteNetMode
from .env import WasteNetEnv
from .ppo import best_config
from .scheduler import WasteNetActivation
from .utils import generate_graph


class WasteNet(Model):
    """Waste collection network model"""

    def __init__(self, mode, nb_nodes=10, nb_episodes=1):

        # Network
        self.G = generate_graph(nb_nodes)
        self.grid = NetworkGrid(self.G)

        # Gym Environment
        env_config = dict(graph=self.G)
        self.env = WasteNetEnv(env_config)

        # RL Agent
        if mode == WasteNetMode.PPO.name:
            rl_agent = PPOAgent("WasteNet", WasteNetEnv, env_config, best_config)
            rl_agent.load("./checkpoints/checkpoint-best")
        else:
            rl_agent = None

        # Scheduler
        self.schedule = WasteNetActivation(self, mode, rl_agent)

        # Data Collector
        self.datacollector = DataCollector(
            model_reporters={
                "Empty": nb_empty,
                "Medium": nb_medium,
                "Full": nb_full,
                "Overflow": nb_overflow,
            },
            agent_reporters={"Fill level (%)": fill_level, "": lambda a: 100},
        )

        # Mesa Agents
        for i, node in enumerate(self.G.nodes()):
            if i in (0, self.G.number_of_nodes() - 1):
                a = BaseAgent(i, self)
            else:
                a = DumpsterAgent(i, self, self.env.fill_levels[i - 1])
            self.schedule.add(a)
            self.grid.place_agent(a, node)

        self.remaining_episodes = nb_episodes
        self.running = True
        self.datacollector.collect(self)

    def step(self):
        done = self.schedule.step()
        self.datacollector.collect(self)
        if done:
            self.env.reset()
            self.remaining_episodes -= 1
        if self.remaining_episodes == 0:
            self.running = False


def nb_empty(model):
    return sum(map(lambda l: l <= 20, model.env.fill_levels))


def nb_medium(model):
    return sum(map(lambda l: l > 20 and l < 80, model.env.fill_levels))


def nb_full(model):
    return sum(map(lambda l: l >= 80 and l < 100, model.env.fill_levels))


def nb_overflow(model):
    return sum(map(lambda l: l == 100, model.env.fill_levels))


def fill_level(agent):
    return getattr(agent, "fill_level", 0)
