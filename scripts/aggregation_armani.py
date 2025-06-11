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
    return math.exp(-beta * n)


class State(Enum):
    WANDERING = 0
    JOINING = 1
    STILL = 2
    LEAVING = 3


@dataclass
class CockroachConfig(Config):
    max_speed: float = 2
    obstacle_weight: float = 80
    alpha: float = 0.4
    beta: float = 0.6
    join_time: int = 50
    leave_time: int = 50
    density_threshold: int = 4


class CockroachAgent(Agent):
    aggregate: bool = False

    config: CockroachConfig

    state: str = 'wandering'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = State.WANDERING
        self.join_timer = 0
        self.leave_timer = 0

    def change_position(self, dt: float = 1.0):
        self.there_is_no_escape()

    def neighbors_in_radius(self):
        return self.in_proximity_accuracy()

    def update(self) -> None:
        if self.on_site() and self.state == 'wandering':
            self.pos += self.move / 2
            self.aggregate = True
        else:
            self.pos += self.move * 2
            self.aggregate = False
        for _ in self.neighbors_in_radius():
            print(_)
        print()


(
    Simulation(
        CockroachConfig(
            image_rotation=True, movement_speed=1, radius=150, seed=1)
    )
    .batch_spawn_agents(
        count=100,
        agent_class=CockroachAgent,
        images=[str(BASE_DIR / "files" / "rainbolt_icon2.png")])
    .spawn_site(
        image_path=str(BASE_DIR / "files" / "circle.png"),
        x=375,
        y=375)
    .run()
)
