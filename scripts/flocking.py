from dataclasses import dataclass
from vi import Agent, Config, Simulation
from config import BASE_DIR
import pygame
Vector2 = pygame.math.Vector2


@dataclass
class FlockingConfig(Config):
    alignment_weight: float = 0.01
    cohesion_weight: float = 1
    separation_weight: float = 100
    obstacle_weight: float = 80
    mass: float = 1
    max_speed: float = 2


class FlockingAgent(Agent):

    config: FlockingConfig

    def change_position(self, dt: float = 1.0):

        a = self.get_alignment()
        c = self.get_cohesion()
        s = self.get_separation()
        w = self.get_obstacle_avoidance()

        f_total = (
            self.config.alignment_weight * a +
            self.config.cohesion_weight * c +
            self.config.separation_weight * s +
            self.config.obstacle_weight * w
        ) / self.config.mass

        self.move += f_total * dt
        if self.move.length() > self.config.max_speed:
            self.move.scale_to_length(self.config.max_speed)

        self.pos += self.move * dt
        self.there_is_no_escape()

    def get_obstacle_avoidance(self) -> Vector2:
        steer = Vector2()
        for hit in self.obstacle_intersections(scale=1.6):
            steer += (self.pos - hit).normalize() / 0.1
        return steer

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

        return cohesion_force

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
        FlockingConfig(
            image_rotation=True, movement_speed=1, radius=150, seed=1)
    )
    .batch_spawn_agents(
        count=100,
        agent_class=FlockingAgent,
        images=[str(BASE_DIR / "files" / "rainbolt_icon2.png")])
    .spawn_obstacle(
        image_path=str(BASE_DIR / "files" / "line.png"),
        x=375,
        y=375)
    .run()
)
