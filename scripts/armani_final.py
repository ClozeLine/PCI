from dataclasses import dataclass
from vi import Agent, Config, Simulation, probability
from pygame.math import Vector2
import random

import seaborn as sns
import matplotlib.pyplot as plt

import polars as pl
import seaborn as sns
import pygame
import numpy

PLANTS = 100
precomputed_angles = [random.uniform(0, 2 * numpy.pi) for _ in range(1000)]


@dataclass
class PredatorPreyConfig(Config):
    prey_speed = 1
    predator_speed = 1

    pred_food_decrease = 0.2
    prey_food_decrease = 0.005

    plant_calories = 20
    prey_calories = 35

    reproduction_cooldown = 100

    max_plants = 150
    pass


class PredatorAgent(Agent):
    config: PredatorPreyConfig

    def __init__(self, images, simulation, pos=None, move=None):
        super().__init__(images, simulation, pos, move)
        self.move = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        self.last_move = self.move
        self.previous_state = "Wandering"
        self.state = "Wandering"
        self.speed = self.config.prey_speed
        self.food = 100
        self.reproduction_cooldown = 0

    def update(self):

        if self.id == 1:
            self.change_image(1)
            if self.previous_state != self.state:
                print(self.state)

        self.reproduction_cooldown = max(self.reproduction_cooldown - 1, 0)

        for other in self.in_proximity_accuracy():
            if isinstance(other[0], PreyAgent):
                if self.pos.distance_to(other[0].pos) <= 20 and not self.on_site():

                    self.food += self.config.prey_calories
                    other[0].kill()

                    predators = 1
                    preys = 1

                    for agent in self.in_proximity_accuracy():
                        if isinstance(agent[0], PreyAgent):
                            preys += 1
                        elif isinstance(agent[0], PredatorAgent):
                            predators += 1

                    reproduction_rate = predators / (predators + preys)

                    if (self.food >= 120
                            and (random.random() > reproduction_rate
                                 and self.reproduction_cooldown == 0)):
                        self.food -= 50
                        self.reproduce()
                        self.reproduction_cooldown = self.config.reproduction_cooldown

        self.save_data("agent", "Predator")

        if self.food <= 0:
            self.kill()

        self.food -= self.config.pred_food_decrease
        self.previous_state = self.state

    def change_position(self):
        self.there_is_no_escape()

        if self.state == "Wandering":

            self.move += Vector2(random.uniform(-1, 1), random.uniform(-1, 1)) * random.uniform(0, 0.3)

            if self.move.length() >= 0.8 and self.move.length() != 0:
                self.move = self.move.normalize()

        else:
            print(f"State Error: state is {self.state}")

        self.last_move = self.move
        self.pos += self.move


class PreyAgent(Agent):
    config: PredatorPreyConfig

    def __init__(self, images, simulation, pos=None, move=None):
        super().__init__(images, simulation, pos, move)
        self.move = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        self.last_move = self.move
        self.previous_state = "Wandering"
        self.state = "Wandering"
        self.speed = self.config.predator_speed
        self.food = 100
        self.reproduction_cooldown = 0

    def update(self):
        global PLANTS

        if self.state == "Wandering":
            pass
        else:
            print(f"State Error: state is {self.state}")

        self.reproduction_cooldown = max(self.reproduction_cooldown - 1, 0)

        for other in self.in_proximity_accuracy():
            if isinstance(other[0], PlantAgent):
                if self.pos.distance_to(other[0].pos) <= 10 and not other[0].eaten:
                    self.food += self.config.plant_calories
                    other[0].eaten = True

                    predators = 1
                    preys = 1

                    for agent in self.in_proximity_accuracy():
                        if isinstance(agent[0], PreyAgent):
                            preys += 1
                        elif isinstance(agent[0], PredatorAgent):
                            predators += 1

                    reproduction_rate = preys / (predators + preys)

                    if (self.food >= 100
                            and (random.random() > reproduction_rate - 0.2)
                            and self.reproduction_cooldown == 0):
                        self.food -= 30
                        self.reproduce()
                        self.reproduction_cooldown = self.config.reproduction_cooldown
                    other[0].kill()
                    PLANTS -= 1

        self.save_data("agent", "Prey")
        if self.id == 11:
            self.change_image(1)
            if self.previous_state != self.state:
                print(self.state)

        if self.food <= 0:
            self.kill()

        self.food -= self.config.prey_food_decrease
        self.previous_state = self.state

    def change_position(self):
        self.there_is_no_escape()

        if self.state == "Wandering":

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
        self.maxCount = 180  #random.randint(190,210)
        self.angle_index = 0
        self.eaten = False

    def update(self):
        global PLANTS
        if self.counter == self.maxCount and PLANTS <= self.config.max_plants:
            self.reproduce()
            PLANTS += 1

            probability = random.random()

            if probability < 0.4:
                if random.random() < 0.5:
                    self.pos = pygame.math.Vector2(random.randint(140, 230), random.randint(140, 230))
                else:
                    self.pos = pygame.math.Vector2(random.randint(515, 595), random.randint(515, 595))
            elif probability >= 0.4 and probability < 0.85:
                self.pos = pygame.math.Vector2(random.randint(0, 750, ), random.randint(0, 750))
            else:
                angle = precomputed_angles[self.angle_index]
                self.angle_index = (self.angle_index + self.id) % len(precomputed_angles)
                direction = pygame.math.Vector2(numpy.cos(angle), numpy.sin(angle))
                self.pos += 10 * direction

            self.counter = 0
        self.save_data("agent", "Plant")
        self.counter += 1

    def change_position(self):
        self.there_is_no_escape()


data = (
    Simulation(
        # TODO: Modify `movement_speed` and `radius` and observe the change in behaviour.
        PredatorPreyConfig(image_rotation=True, movement_speed=1, radius=150, seed=1, fps_limit=60, duration=20000)

    )
    .spawn_site("../files/circle.png", 185, 185)
    .spawn_site("../files/circle.png", 560, 560)
    .batch_spawn_agents(10, PredatorAgent, images=["../files/Target1.png", "../files/Target6.png"])
    .batch_spawn_agents(100, PreyAgent, images=["../files/triangle.png", "../files/Target5.png"])
    .batch_spawn_agents(PLANTS, PlantAgent, images=["../files/plant.png"])
    .run()
    .snapshots
)

frame_window = 10
summary = (
    data.filter(pl.col("frame") % 60 == 0)
        .with_columns((pl.col("frame") // 60).alias("second"))
        .group_by("second")
        .agg([
            pl.col("agent").filter(pl.col("agent") == "Predator").count()
                            .alias("predator_count"),
            pl.col("agent").filter(pl.col("agent") == "Prey").count()
                            .alias("prey_count"),
        ])
        .sort("second")
        .with_columns([
            (pl.col("predator_count") * 2)
                .alias("predator_plot"),
            (pl.col("predator_count") * 2)
                .rolling_mean(window_size=frame_window, min_samples=1)
                .alias("predator_smooth"),
            pl.col("prey_count")
                .rolling_mean(window_size=frame_window, min_samples=1)
                .alias("prey_smooth"),
        ])
)

sns.lineplot(summary, x='second', y='predator_smooth', label='Predator (x2, smooth)')
sns.lineplot(summary, x='second', y='prey_smooth',    label='Prey (smooth)')
plt.xlabel('Second')
plt.ylabel('Count')
plt.legend()
plt.show()
