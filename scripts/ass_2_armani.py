# animal's speed depends on their energy level
# genetic selection: start with random, see who gets eliminated. Some factors could be:
# - max speed
# - appetite
# - willingness to breed (rabbits)
# rabbit can eat poisonous berries, get infected, and contaminate fox (if eaten)

from dataclasses import dataclass
from vi import Agent, Config, Simulation
from pygame.math import Vector2
import random
from enum import Enum
import polars as pl
import pygame
import numpy

precomputed_angles = [random.uniform(0, 2 * numpy.pi) for _ in range(1000)]
PLANT_COUNTER = 10
PREY_COUNTER = 100
PREDATOR_COUNTER = 10


def calc_LJ_force(distance, epsilon=100, sigma=0.01):
    if distance == 0:
        return 0
    return 24 * epsilon * (2 * (sigma / distance) ** 13 - (sigma / distance) ** 7)


@dataclass
class PredatorPreyConfig(Config):
    # general
    max_food = 100
    start_food = max_food * 0.7

    # predator config
    predator_speed = 1
    attack_speed_increase = 1.3
    predator_food_on_eat = 45

    # prey config
    prey_speed = 1
    escape_speed_increase = 1.3
    prey_food_on_eat = 10

    # plant
    max_plants = 150


class PredatorState(Enum):
    WANDERING = 0
    CHASING = 1


class PreyState(Enum):
    WANDERING = 0
    FLEEING = 1


class PredatorAgent(Agent):
    config: PredatorPreyConfig

    def __init__(self, images, simulation, pos=None, move=None):
        super().__init__(images, simulation, pos, move)
        self.move = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        self.last_move = self.move
        self.previous_state = PredatorState.WANDERING
        self.state = PredatorState.WANDERING
        self.speed = self.config.prey_speed
        self.food = self.config.max_food

    def update(self):
        global PREDATOR_COUNTER, PREY_COUNTER

        for agent in self.in_proximity_accuracy():
            if isinstance(agent[0], PreyAgent):
                if self.pos.distance_to(agent[0].pos) <= 10:
                    self.food += self.config.predator_food_on_eat
                    agent[0].kill()
                    PREY_COUNTER -= 1
                    if self.food > self.config.max_food:
                        self.food = self.config.max_food
                        self.reproduce()
                        PREDATOR_COUNTER += 1

        if self.food <= 0:
            self.kill()
            PREDATOR_COUNTER -= 1

        self.food -= 0.3
        self.previous_state = self.state

    def calculate_speed(self):
        factor = (self.food / self.config.max_food) * 100
        return self.move

    def change_position(self):
        self.there_is_no_escape()

        if self.state == PredatorState.WANDERING:

            self.move += Vector2(random.uniform(-1, 1), random.uniform(-1, 1)) * random.uniform(0, 0.3)

            if self.move.length() >= 0.8 and self.move.length() != 0:
                self.move = self.move.normalize()

        self.last_move = self.move
        self.pos += self.calculate_speed()


class PreyAgent(Agent):
    config: PredatorPreyConfig

    def __init__(self, images, simulation, pos=None, move=None):
        super().__init__(images, simulation, pos, move)
        self.move = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        self.last_move = self.move
        self.previous_state = PreyState.WANDERING
        self.state = PreyState.WANDERING
        self.speed = self.config.predator_speed
        self.food = self.config.max_food

    def update(self):
        global PLANT_COUNTER, PREY_COUNTER

        if self.state == PreyState.WANDERING:
            pass

        for agent in self.in_proximity_accuracy():
            if isinstance(agent[0], PlantAgent):
                if self.pos.distance_to(agent[0].pos) <= 10:
                    self.food += self.config.prey_food_on_eat
                    if self.food > self.config.max_food:
                        self.food = self.config.max_food
                        self.reproduce()
                        PREY_COUNTER += 1
                    agent[0].kill()
                    PLANT_COUNTER -= 1

        if self.food <= 0:
            self.kill()
            PREY_COUNTER -= 1

        self.food -= 0.1
        self.previous_state = self.state

    def change_position(self):
        self.there_is_no_escape()

        if self.state == PreyState.WANDERING:

            self.move += Vector2(random.uniform(-1, 1), random.uniform(-1, 1)) * random.uniform(0, 0.3)

            if self.move.length() >= 0.8 and self.move.length() != 0:
                self.move = self.move.normalize()

        else:
            print(f"State Error: state is {self.state}")

        self.last_move = self.move
        self.pos += self.move


class PlantAgent(Agent):
    config: PredatorPreyConfig

    def __init__(self, images, simulation, pos=None, move=None):
        super().__init__(images, simulation, pos, move)
        self.counter = 0
        self.angle_index = 0

    def update(self):
        global PLANT_COUNTER
        print(PLANT_COUNTER)
        if self.counter == self.config.max_food and PLANT_COUNTER < self.config.max_plants:
            self.reproduce()
            PLANT_COUNTER += 1

            if random.random() < 0.5:
                self.pos = pygame.math.Vector2(random.randint(0, 750, ), random.randint(0, 750))
            else:
                angle = precomputed_angles[self.angle_index]
                self.angle_index = (self.angle_index + self.id) % len(precomputed_angles)
                direction = pygame.math.Vector2(numpy.cos(angle), numpy.sin(angle))
                self.pos += 10 * direction

            self.counter = 0
        self.counter += 1

    def change_position(self):
        pass


(
    Simulation(
        # TODO: Modify `movement_speed` and `radius` and observe the change in behaviour.
        PredatorPreyConfig(image_rotation=True, movement_speed=1, radius=50, seed=1, fps_limit=60, ),  # duration=10 *60

    )

    .batch_spawn_agents(PREDATOR_COUNTER, PredatorAgent, images=["../files/Target1.png", "../files/Target6.png"])
    .batch_spawn_agents(PREY_COUNTER, PreyAgent, images=["../files/triangle.png", "../files/Target5.png"])
    .batch_spawn_agents(PLANT_COUNTER, PlantAgent, images=["../files/plant.png"])
    .run()
)

# countDataFrame = pl.DataFrame(countList)
# print(countDataFrame)

# plot = sns.relplot(countDataFrame, x=countDataFrame['column_0'], y=countDataFrame['column_1'])
# plot.savefig('agents.png', dpi=300)