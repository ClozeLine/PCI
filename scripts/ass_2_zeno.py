from dataclasses import dataclass
from vi import Agent, Config, Simulation
from config import BASE_DIR
from enum import Enum
import math, random
from pygame.math import Vector2
from random import randint

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
class FoxConfig(Config):
    max_speed: float = 2
    obstacle_weight: float = 80
    alpha: float = 0.001
    beta: float = 0.6
    join_time: int = 5
    leave_time: int = 6
    density_threshold: int = 4

@dataclass
class RabbitConfig(Config):
    max_speed: float = 2
    obstacle_weight: float = 80
    alpha: float = 0.001
    beta: float = 0.6
    join_time: int = 5
    leave_time: int = 6
    density_threshold: int = 4


class FoxAgent(Agent):
    config: FoxConfig

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.join_timer = 0
        self.leave_timer = 0

    def change_position(self, dt: float = 1.0):
        angle = randint(0, 360)
        rand_vec = Vector2(1, 0).rotate(angle) * dt

        self.pos += self.move
        self.pos += rand_vec
        self.there_is_no_escape()

    def neighbors_in_radius(self):
        return self.in_proximity_performance()

    
    def update(self) -> None:
        
        for neighbour in self.neighbors_in_radius():
            pos_a = self.pos
            pos_b = neighbour.pos
            dis = pos_a.distance_to(pos_b)

            if type(neighbour) == Rabbit and dis < 35:
                neighbour.kill()
                print(dis)
                self.reproduce()
                
                

class Rabbit(Agent):
    config: FoxConfig

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.join_timer = 0
        self.leave_timer = 0

    def change_position(self, dt: float = 1.0):
        angle = randint(0, 360)
        rand_vec = Vector2(1, 0).rotate(angle) * dt

        self.pos += self.move
        self.pos += rand_vec
        self.there_is_no_escape()


    def update(self) -> None:
    
        if random.random() <= 0.005:
            self.reproduce()
        


(
    Simulation(
        FoxConfig(
            image_rotation=True, movement_speed=2, radius=100)
    )
    .batch_spawn_agents(
        count=5,
        agent_class=FoxAgent,
        images=[str(BASE_DIR / "files" / "rainbolt_icon2.png")])
    .batch_spawn_agents(
        count=5,
        agent_class=Rabbit,
        images=[str(BASE_DIR / "files" / "triangle_.png")])
    .run()
)
