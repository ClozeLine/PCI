# animal's speed depends on their energy level
# rabbit can eat poisonous berries, get infected, and contaminate fox (if eaten)

from dataclasses import dataclass
from vi import Agent, Config, Simulation
from pygame.math import Vector2
import random
from enum import Enum
import polars as pl
import seaborn as sns
import pygame
import numpy
import matplotlib.pyplot as plt

precomputed_angles = [random.uniform(0, 2 * numpy.pi) for _ in range(1000)]
PLANT_COUNTER = 35
PREY_COUNTER = 60
PREDATOR_COUNTER = 20

database_prey = [
    {"frame": 0, "count": PREY_COUNTER}
]
database_predator = [
    {"frame": 0, "count": PREDATOR_COUNTER}
]


@dataclass
class PredatorPreyConfig(Config):
    # general
    start_food = 100
    max_speed = 2
    reproduction_cooldown = 200

    # predator config
    predator_speed = 1
    predator_food_decrease = 0.2
    predator_food_on_eat = 60
    predator_chasing_speed_increase = 1.4

    # prey config
    prey_speed = 1
    prey_food_decrease = 0.05
    prey_food_on_eat = 5
    prey_fleeing_speed_increase = 1.1

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
        self.reproduction_cooldown: int = self.config.reproduction_cooldown
        self.previous_state = PredatorState.WANDERING
        self.state = PredatorState.WANDERING
        self.speed = self.config.prey_speed
        self.food = self.config.start_food

    def update(self):
        global PREDATOR_COUNTER, PREY_COUNTER
        print(PREY_COUNTER)

        self.state = PredatorState.WANDERING
        self.reproduction_cooldown = max(self.reproduction_cooldown - 1, 0)

        for agent in self.in_proximity_accuracy():
            if isinstance(agent[0], PreyAgent):
                dist_to_prey = self.pos.distance_to(agent[0].pos)
                if dist_to_prey <= 10 and agent[0].alive:
                    self.food += self.config.predator_food_on_eat
                    agent[0].kill()
                    PREY_COUNTER -= 1
                    if (self.food > 120
                            and self.reproduction_cooldown == 0 and PREY_COUNTER <= 100):
                        self.reproduce()
                        PREDATOR_COUNTER += 1
                        self.reproduction_cooldown = self.config.reproduction_cooldown
                if 10 < dist_to_prey <= 50:
                    self.state = PredatorState.CHASING
                    self.move = (agent[0].pos - self.pos).normalize()
                    break

        if self.food <= 0:
            self.kill()
            PREDATOR_COUNTER -= 1

        self.food -= self.config.predator_food_decrease
        self.previous_state = self.state

        last_frame_nr = database_predator[-1]["frame"]
        new_entry = {"frame": last_frame_nr + 1, "count": PREDATOR_COUNTER}
        database_predator.append(new_entry)

        self.save_data("PredCount", PREDATOR_COUNTER)
        self.save_data("PreyCount", PREY_COUNTER)

    def calculate_speed(self):
        if self.move.length() > 0:
            self.move = self.move.normalize()

        speed = 1
        if self.state == PredatorState.CHASING:
            speed *= self.config.predator_chasing_speed_increase

        speed = min(speed, self.config.max_speed)

        return self.move * speed

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
    HUNGER_THRESHOLD = 0.6
    REPRO_COST = 35

    def __init__(self, images, simulation, pos=None, move=None):
        super().__init__(images, simulation, pos, move)
        self.move = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        self.reproduction_cooldown = self.config.reproduction_cooldown
        self.state = PreyState.WANDERING
        self.food = self.config.start_food
        self.alive = True

    def update(self):
        global PLANT_COUNTER, PREY_COUNTER

        # reproduction cooldown
        self.reproduction_cooldown = max(self.reproduction_cooldown - 1, 0)

        predator, plant = None, None
        pred_dist, plant_dist = float("inf"), float("inf")

        for other, _ in self.in_proximity_accuracy():
            if isinstance(other, PredatorAgent):
                d = self.pos.distance_to(other.pos)
                if d < pred_dist and d <= 50:
                    predator, pred_dist = other, d

            elif isinstance(other, PlantAgent) and not getattr(other, "eaten", False):
                d = self.pos.distance_to(other.pos)
                if d < plant_dist:
                    plant, plant_dist = other, d

        # decide if hungry
        hungry = self.food_ratio() < self.HUNGER_THRESHOLD

        # flee -> priority
        if predator:
            self.state = PreyState.FLEEING
            self.move = (self.pos - predator.pos).normalize()

        # eat
        elif hungry and plant and plant_dist <= 50:
            self.state = PreyState.EATING
            self.move = (plant.pos - self.pos).normalize()

            # eat if close enough
            if plant_dist <= 10 and not plant.eaten:
                plant.eaten = True
                plant.kill()
                PLANT_COUNTER -= 1

                self.food += self.config.prey_food_on_eat

        # wander
        else:
            self.state = PreyState.WANDERING

        # reproduce
        if (self.food >= 100 and
                self.reproduction_cooldown == 0 and PREY_COUNTER <= 200):
            self.food -= self.REPRO_COST
            self.reproduce()
            PREY_COUNTER += 1
            self.reproduction_cooldown = self.config.reproduction_cooldown

        # maybe die
        self.food -= self.config.prey_food_decrease
        if self.food <= 0:
            self.kill()
            PREY_COUNTER -= 1

        last_frame_nr = database_prey[-1]["frame"]
        new_entry = {"frame": last_frame_nr + 1, "count": PREY_COUNTER}
        database_prey.append(new_entry)

        self.save_data("PredCount", PREDATOR_COUNTER)
        self.save_data("PreyCount", PREY_COUNTER)

    def calculate_speed(self):
        new_move = self.move
        if self.state == PreyState.FLEEING:
            new_move *= self.config.prey_fleeing_speed_increase
        if new_move.length() > self.config.max_speed:
            new_move = new_move.normalize() * self.config.max_speed
        return new_move

    def food_ratio(self):
        return self.food / self.config.start_food

    def change_position(self):
        self.there_is_no_escape()

        if self.state == PreyState.WANDERING:
            self.move += Vector2(
                random.uniform(-1, 1),
                random.uniform(-1, 1)
            ) * random.uniform(0, 0.3)
            if self.move.length() >= 0.8:
                self.move = self.move.normalize()
        self.pos += self.calculate_speed()

    def kill(self):
        if self.alive:
            self.alive = False
            super().kill()


class PlantAgent(Agent):
    config: PredatorPreyConfig

    def __init__(self, images, simulation, pos=None, move=None):
        super().__init__(images, simulation, pos, move)
        self.counter = 0
        self.angle_index = 0
        self.reproduction_threshold = random.randint(8, 25)
        self.eaten = False

    def update(self):
        global PLANT_COUNTER
        if self.counter >= self.reproduction_threshold and PLANT_COUNTER < self.config.max_plants:
            self.reproduce()
            PLANT_COUNTER += 1

            if random.random() < 0.7:
                angle = random.uniform(0, 2 * numpy.pi)
                offset = pygame.Vector2(numpy.cos(angle), numpy.sin(angle)) * random.uniform(5, 30)
                self.pos += offset
            else:
                self.pos = Vector2(random.randint(0, 750), random.randint(0, 750))
            self.counter = 0
        self.counter += 1

        self.save_data("PredCount", PREDATOR_COUNTER)
        self.save_data("PreyCount", PREY_COUNTER)

    def change_position(self):
        pass


class PlantSpawner(PlantAgent):

    MIN_PLANTS = 50
    BURST_SIZE = 7
    CHECK_EVERY = 30

    def update(self):
        global PLANT_COUNTER

        super().update()

        if self.counter % self.CHECK_EVERY == 0 and PLANT_COUNTER < self.MIN_PLANTS:
            seeds = min(self.BURST_SIZE,
                        self.config.max_plants - PLANT_COUNTER)

            for _ in range(seeds):
                new_plant = self.reproduce()
                PLANT_COUNTER += 1

                new_plant.pos = pygame.Vector2(
                    random.randint(0, 750),
                    random.randint(0, 750)
                )

            self.counter = 0


data = (
    Simulation(
        # TODO: Modify `movement_speed` and `radius` and observe the change in behaviour.
        PredatorPreyConfig(
            image_rotation=True,
            movement_speed=1,
            radius=50,
            seed=1,
            fps_limit=60,
            duration=3000),

    )

    .batch_spawn_agents(PREDATOR_COUNTER, PredatorAgent, images=["../files/Target1.png", "../files/Target6.png"])
    .batch_spawn_agents(PREY_COUNTER, PreyAgent, images=["../files/triangle.png", "../files/Target5.png"])
    .batch_spawn_agents(PLANT_COUNTER, PlantAgent, images=["../files/plant.png"])
    .run().snapshots
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

sns.lineplot(summary, x='second', y='predator_smooth', label='Predator (x2)')
sns.lineplot(summary, x='second', y='prey_smooth',    label='Prey')
plt.xlabel('Second')
plt.ylabel('Count')
plt.legend()
plt.show()
