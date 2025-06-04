from dataclasses import dataclass
from pathlib import Path

from vi import Agent, Config, Simulation
from scripts.config import BASE_DIR


@dataclass
class FlockingConfig(Config):
    # TODO: Modify the weights and observe the change in behaviour.
    alignment_weight: float = 1
    cohesion_weight: float = 1
    separation_weight: float = 1


class FlockingAgent(Agent[FlockingConfig]):
    # By overriding `change_position`, the default behaviour is overwritten.
    # Without making changes, the agents won't move.
    def change_position(self):
        self.there_is_no_escape()

        # TODO: Modify self.move and self.pos accordingly.


(
    Simulation(
        # TODO: Modify `movement_speed` and `radius` and observe the change in behaviour.
        FlockingConfig(
            image_rotation=True, movement_speed=1, radius=50, seed=1)
    )
    .batch_spawn_agents(
        count=100,
        agent_class=FlockingAgent,
        images=BASE_DIR / "files" / "rainbolt_logo.png")
    .run()
)
