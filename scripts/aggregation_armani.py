from dataclasses import dataclass
from vi import Agent, Config, Simulation
from config import BASE_DIR

# idea for extra: make the agent FOV an angle, not a radius

# possible states:
# - wandering (rand. walk)
# - joining (join aggr.)
# - still (stop in aggr.)
# - leave (start wandering after join)

# start wandering, then joining when site sensed (probability P-join -> takes into account n sites in range)
# after joining, stays still after T-still time


config = Config()
x, y = config.window.as_tuple()


@dataclass
class CockroachConfig(Config):
    max_speed: float = 2
    obstacle_weight: float = 80


class CockroachAgent(Agent):

    config: CockroachConfig

    def change_position(self, dt: float = 1.0):
        self.pos += self.move
        self.there_is_no_escape()


(
    Simulation(
        CockroachConfig(
            image_rotation=True, movement_speed=1, radius=150, seed=1)
    )
    .batch_spawn_agents(
        count=100,
        agent_class=CockroachAgent,
        images=[str(BASE_DIR / "files" / "rainbolt_icon2.png")])
    .spawn_obstacle(
        image_path=str(BASE_DIR / "files" / "circle.png"),
        x=375,
        y=375)
    .run()
)
