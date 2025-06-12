from dataclasses import dataclass
from vi import Agent, Config, Simulation
from vi.simulation import Shared
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
    alpha: float = 0.001
    beta: float = 0.6
    join_time: int = 5
    leave_time: int = 6
    density_threshold: int = 4

site_count = 0


class CockroachAgent(Agent):
    config: CockroachConfig


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = State.WANDERING
        self.join_timer = 0
        self.leave_timer = 0
        self.time = 0
        self.shared.site_count_0 = 0
        self.shared.site_count_1 = 0
        self.updated = False
        self.migrated = False
        self.wrong_spot = None

    def count_sites(self):
        return self._sites

    def change_position(self, dt: float = 1.0):
        self.there_is_no_escape()

    def neighbors_in_radius(self):
        return self.in_proximity_performance()

    def update(self) -> None:

        self.time += 1

        if self.time >= 2000 and self.on_site() and self.updated == False:
            if self.on_site_id() == 0:
                self.shared.site_count_0 += 1
            else:
                self.shared.site_count_1 += 1

            self.updated = True

        if self.time >= 2002 and self.on_site_id() == 0 and self.migrated == False:
            if self.shared.site_count_0 < 50:
                self.state = State.LEAVING

            self.migrated = True

            self.wrong_spot = 0

        elif self.time >= 2002 and self.on_site_id() == 1 and self.migrated == False:
            if self.shared.site_count_1 < 50:
                self.state = State.LEAVING

            self.migrated = True
            self.wrong_spot = 1

        """
        self.time += 0

        if self.time == 150 and self.on_site():
            #self.shared.site_count += 1
            site_id = self.on_site_id()
            if site_id != 0:
                print(site_id)

        if self.time > 150:
            print(self.shared.site_count)
        """
        
        neighbors_in_rad: int = 0
        for _ in self.neighbors_in_radius():
            neighbors_in_rad += 1
        inside_site = self.on_site()
        sites_exist = True if self.count_sites() else False

        # wandering
        if self.state is State.WANDERING:
            self.pos += self.move
            if sites_exist and inside_site and random.random() < p_join(neighbors_in_rad, self.config.alpha):

                if self.on_site_id() != self.wrong_spot:
                    self.state = State.JOINING
                    self.join_timer = self.config.join_time

        # joining
        elif self.state is State.JOINING:
            if not inside_site:
                self.state = State.WANDERING
                return
            self.pos += self.move
            self.join_timer -= 1
            if self.join_timer <= 0:
                self.state = State.STILL

        # still
        elif self.state is State.STILL:
            if not inside_site:
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
            image_rotation=True, movement_speed=2, radius=150)
    )
    .spawn_site(
        image_path=str(BASE_DIR / "files" / "circle_big.png"),
        x=200,
        y=375)
    .spawn_site(
        image_path=str(BASE_DIR / "files" / "circle_big.png"),
        x=575,
        y=375)
    .batch_spawn_agents(
        count=100,
        agent_class=CockroachAgent,
        images=[str(BASE_DIR / "files" / "rainbolt_icon2.png")])
    .run()
)
