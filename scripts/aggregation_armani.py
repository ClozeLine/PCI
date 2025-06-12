from dataclasses import dataclass
from vi import Agent, Config, Simulation
from config import BASE_DIR
from enum import Enum
import math, random

# idea for extra: make the agent FOV an angle, not a radius

# possible states:
# - wandering (rand. walk)
# - joining (join aggr.)
# - still (stop in aggr.)
# - leave (start wandering after join)

# start wandering, then joining when site sensed (probability P-join -> takes into account n sites in range)
# after joining, stays still after T-still time

# run min. 30 times (maybe change the seed each time)

config = Config()
x, y = config.window.as_tuple()
print(x, y)


def p_join(n, alpha):
    return 1 - math.exp(-alpha * n)


def p_leave(n, beta):
    return math.exp(-beta * n**2)


class State(Enum):
    WANDERING = 0
    JOINING = 1
    STILL = 2
    LEAVING = 3


@dataclass
class CockroachConfig(Config):
    max_speed: float = 2
    obstacle_weight: float = 80
    alpha: float = 0.5
    beta: float = 0.6
    join_time: int = 5
    leave_time: int = 6
    density_threshold: int = 4


class CockroachAgent(Agent):
    config: CockroachConfig

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = State.WANDERING
        self.join_timer = 0
        self.leave_timer = 0

    def count_sites(self):
        return self._sites

    def change_position(self, dt: float = 1.0):
        self.there_is_no_escape()

    def neighbors_in_radius(self):
        return self.in_proximity_performance()

    def update(self) -> None:
        neighbors_in_rad: int = 0
        for _ in self.neighbors_in_radius():
            neighbors_in_rad += 1
        inside_site = self.on_site()
        sites_exist = True if self.count_sites() else False
        site_like = inside_site if sites_exist else (neighbors_in_rad >= self.config.density_threshold)
        is_on_cluster = inside_site or (not sites_exist and neighbors_in_rad >= self.config.density_threshold)

        # wandering
        if self.state is State.WANDERING:
            self.pos += self.move
            if is_on_cluster and random.random() < p_join(neighbors_in_rad, self.config.alpha):
                self.state = State.JOINING
                self.join_timer = self.config.join_time

        # joining
        elif self.state is State.JOINING:
            if not is_on_cluster:
                self.state = State.WANDERING
                return
            self.pos += self.move
            self.join_timer -= 1
            if self.join_timer <= 0:
                self.state = State.STILL

        # still
        elif self.state is State.STILL:
            if not is_on_cluster:
                self.state = State.WANDERING
                return
            self.freeze_movement()

            if random.random() < p_leave(neighbors_in_rad, self.config.beta):
                self.state = State.LEAVING
                self.leave_timer = self.config.leave_time

        # leaving
        elif self.state is State.LEAVING:
            self.pos += self.move
            self.leave_timer -= 1
            if self.leave_timer <= 0:
                self.state = State.WANDERING


(
    Simulation(
        CockroachConfig(
            image_rotation=True, movement_speed=2, radius=50, seed=1)
    )
    .spawn_site(
        image_path=str(BASE_DIR / "files" / "circle_big.png"),
        x=200,
        y=375)
    .spawn_site(
        image_path=str(BASE_DIR / "files" / "circle.png"),
        x=575,
        y=375)
    .batch_spawn_agents(
        count=100,
        agent_class=CockroachAgent,
        images=[str(BASE_DIR / "files" / "rainbolt_icon2.png")])
    .run()
)
