import random
from dataclasses import dataclass
import numpy as np
from vi.config import deserialize
from vi import Agent, Config, Simulation
from config import BASE_DIR
import pygame
Vector2 = pygame.math.Vector2


@dataclass
@deserialize
class FlockingConfig(Config):
    alignment_weight: float = 0.1
    cohesion_weight: float = 0.1
    separation_weight: float = 20
    mass: float = 1
    max_speed: float = 2


class FlockingAgent(Agent):

    config: FlockingConfig

    def change_position(self):

        a = self.get_alignment()
        c = self.get_cohesion()
        s = self.get_separation()

        f_total = (self.config.alignment_weight*a + self.config.cohesion_weight*c
                   + self.config.separation_weight*s) / self.config.mass

        self.move += f_total

        if self.move.length() > self.config.max_speed:
            self.move.scale_to_length(self.config.max_speed)

        self.pos += self.move

        self.there_is_no_escape()

    def get_alignment(self):
        neighbour_move = [
            agent.move
            for agent in self.in_proximity_performance()
            if agent is not self
        ]
        if not neighbour_move:
            return Vector2()

        v_mean = sum(neighbour_move, Vector2()) / len(neighbour_move)
        return v_mean - self.move

    def get_cohesion(self):
        neighbour_pos = [
            agent.pos
            for agent in self.in_proximity_performance()
            if agent is not self
        ]
        if not neighbour_pos:
            return Vector2()

        centre = sum(neighbour_pos, Vector2()) / len(neighbour_pos)
        cohesion_force = centre - self.pos

        return cohesion_force - self.move

    def get_separation(self):
        force = Vector2()
        for agent in self.in_proximity_performance():
            if agent is self:
                continue
            offset = self.pos - agent.pos
            dist_sq = offset.length_squared() or 1
            force += offset / dist_sq
        return force


(
    Simulation(
        # TODO: Modify `movement_speed` and `radius` and observe the change in behaviour.
        FlockingConfig(
            image_rotation=True, movement_speed=1, radius=50, seed=1)
    )
    .batch_spawn_agents(
        count=100,
        agent_class=FlockingAgent,
        images=[str(BASE_DIR / "files" / "rainbolt_icon2.png")])
    .run()
)
