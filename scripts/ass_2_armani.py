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
PLANT_COUNTER = 35
PREY_COUNTER = 100
PREDATOR_COUNTER = 20


@dataclass
class PredatorPreyConfig(Config):
    # general
    max_food = 100
    start_food = max_food * 0.7

    # predator config
    predator_speed = 1
    predator_food_decrease = 0.1
    predator_food_on_eat = 20
    predator_chasing_speed_increase = 1.5

    # prey config
    prey_speed = 2
    prey_food_decrease = 0.05
    prey_food_on_eat = 10
    prey_fleeing_speed_increase = 1.5

    # plant
    max_plants = 200


class PredatorState(Enum):
    WANDERING = 0
    CHASING = 1


class PreyState(Enum):
    WANDERING = 0
    FLEEING = 1
    EATING = 2


class PredatorAgent(Agent):
    config: PredatorPreyConfig

    def __init__(self, images, simulation, pos=None, move=None):
        super().__init__(images, simulation, pos, move)
        self.move = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        self.last_move = self.move
        self.reproduction_cooldown: int = 0
        self.previous_state = PredatorState.WANDERING
        self.state = PredatorState.WANDERING
        self.speed = self.config.prey_speed
        self.food = self.config.max_food

    def update(self):
        global PREDATOR_COUNTER, PREY_COUNTER

        if self.reproduction_cooldown > 0:
            self.reproduction_cooldown -= 1

        for agent in self.in_proximity_accuracy():
            if isinstance(agent[0], PreyAgent):
                dist_to_prey = self.pos.distance_to(agent[0].pos)
                if dist_to_prey <= 10:
                    self.food += self.config.predator_food_on_eat
                    agent[0].kill()
                    PREY_COUNTER -= 1
                    if self.food > self.config.max_food and self.reproduction_cooldown == 0:
                        self.food = self.config.max_food
                        self.reproduce()
                        PREDATOR_COUNTER += 1
                        self.reproduction_cooldown = 200
                if 10 < dist_to_prey <= 50:
                    self.state = PredatorState.CHASING
                    self.move = (agent[0].pos - self.pos).normalize()
                    break

        if self.food <= 0:
            self.kill()
            PREDATOR_COUNTER -= 1

        self.food -= self.config.predator_food_decrease
        self.previous_state = self.state

    def calculate_speed(self):
        x = self.food / self.config.max_food
        new_move = self.move * (0.8 + (1 - 0.8) * (x ** 2))
        if self.state == PredatorState.CHASING:
            new_move *= self.config.predator_chasing_speed_increase
        return new_move

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
        self.reproduction_cooldown: int = 0
        self.last_move = self.move
        self.previous_state = PreyState.WANDERING
        self.state = PreyState.WANDERING
        self.speed = self.config.predator_speed
        self.food = self.config.max_food

    def update(self):
        global PLANT_COUNTER, PREY_COUNTER

        self.previous_state = self.state
        self.state = PreyState.WANDERING

        nearest_predator = None
        nearest_plant = None
        min_pred_dist = float("inf")
        min_plant_dist = float("inf")

        if self.reproduction_cooldown > 0:
            self.reproduction_cooldown -= 1

        for agent in self.in_proximity_accuracy():
            other = agent[0]
            if isinstance(other, PredatorAgent):
                dist = self.pos.distance_to(other.pos)
                if dist < min_pred_dist and dist <= 50:
                    nearest_predator = other
                    min_pred_dist = dist
            if isinstance(other, PlantAgent):
                dist = self.pos.distance_to(other.pos)
                if dist < min_plant_dist:
                    nearest_plant = other
                    min_plant_dist = dist

            # either avoid predator, or move towards food
            if nearest_predator:
                self.state = PreyState.FLEEING
                self.move = (self.pos - nearest_predator.pos).normalize()
            elif nearest_plant and min_plant_dist <= 50:
                self.state = PreyState.EATING
                self.move = (nearest_plant.pos - self.pos).normalize()

            # try to eat if close to plant
            if nearest_plant and self.pos.distance_to(nearest_plant.pos) <= 10:
                self.food += self.config.prey_food_on_eat
                if self.food > self.config.max_food and self.reproduction_cooldown == 0:
                    self.food = self.config.max_food
                    self.reproduce()
                    PREY_COUNTER += 1
                    self.reproduction_cooldown = 200
                nearest_plant.kill()
                PLANT_COUNTER -= 1

        # starvation
        if self.food <= 0:
            self.kill()
            PREY_COUNTER -= 1

        self.food -= self.config.prey_food_decrease
        self.previous_state = self.state

    def calculate_speed(self):
        x = self.food / self.config.max_food
        new_move = self.move * (0.6 + (1 - 0.6) * (x ** 2))
        if self.state == PreyState.FLEEING:
            new_move *= self.config.prey_fleeing_speed_increase
        return new_move

    def change_position(self):
        self.there_is_no_escape()

        if self.state == PreyState.WANDERING:

            self.move += Vector2(random.uniform(-1, 1), random.uniform(-1, 1)) * random.uniform(0, 0.3)

            if self.move.length() >= 0.8 and self.move.length() != 0:
                self.move = self.move.normalize()

        self.last_move = self.move
        self.pos += self.calculate_speed()


class PlantAgent(Agent):
    config: PredatorPreyConfig

    def __init__(self, images, simulation, pos=None, move=None):
        super().__init__(images, simulation, pos, move)
        self.counter = 0
        self.angle_index = 0
        self.reproduction_threshold = random.randint(100, 300)

    def update(self):
        global PLANT_COUNTER
        if self.counter >= self.reproduction_threshold and PLANT_COUNTER < self.config.max_plants:
            self.reproduce()
            PLANT_COUNTER += 1
            print(PLANT_COUNTER)

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