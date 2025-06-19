from dataclasses import dataclass
from vi import Agent, Config, Simulation
from pygame.math import Vector2
import random

import polars as pl
import seaborn as sns
import pygame
import numpy



precomputed_angles = [random.uniform(0, 2 * numpy.pi) for _ in range(1000)]

def calc_LJ_force(distance, epsilon=100, sigma=0.01):
    if distance == 0:
        return 0  # Avoid division by zero
    return 24 * epsilon * (2 * (sigma / distance)**13 - (sigma / distance)**7)


@dataclass
class PredatorPreyConfig(Config):
    prey_speed = 1
    predator_speed = 1
    pass


class PredatorAgent(Agent):
    def __init__(self, images, simulation, pos = None, move = None):
        super().__init__(images, simulation, pos, move)
        self.move = pygame.Vector2(random.uniform(-1,1),random.uniform(-1,1))
        self.last_move = self.move
        self.previous_state = "Wandering"
        self.state = "Wandering"
        self.speed = self.config.prey_speed
        self.food = 100

    def update(self):
        
        
        if self.id == 1:
            self.change_image(1)
            #print(pygame.mouse.get_pos())
            if self.previous_state != self.state:
                print(self.state)
        
        for other in self.in_proximity_accuracy():
            if type(other[0]) == PreyAgent:
                if self.pos.distance_to(other[0].pos) <= 10:
                    
                    self.food += 75
                    other[0].kill()
                    if self.food >= 150:
                        self.food -= 50
                        self.reproduce()

        self.save_data("agent", "Predator")

        if self.food <= 0:
            self.kill()

        self.food -= 0.25
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
    CALORIES_GAINED: int = 15
    def __init__(self, images, simulation, pos = None, move = None):
        super().__init__(images, simulation, pos, move)
        self.move = pygame.Vector2(random.uniform(-1,1),random.uniform(-1,1))
        self.last_move = self.move
        self.previous_state = "Wandering"
        self.state = "Wandering"
        self.speed = self.config.predator_speed
        self.food = 100
    
    
    def update(self):

        if self.state == "Wandering":
            pass
        

        else:
            print(f"State Error: state is {self.state}")
        
        for other in self.in_proximity_accuracy():
            if type(other[0]) == PlantAgent:
                if self.pos.distance_to(other[0].pos) <= 10:
                    #print("plant")
                    self.food += self.CALORIES_GAINED
                    if self.food >= 150:
                        self.food -= 50
                        self.reproduce()
                    other[0].kill()

        self.save_data("agent", "Prey")
        if self.id == 11:
            self.change_image(1)
            #print(pygame.mouse.get_pos())
            if self.previous_state != self.state:
                print(self.state)

        if self.food <= 0:
            self.kill()
        

        self.food -= 0.1
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
    def __init__(self, images, simulation, pos = None, move = None):
        super().__init__(images, simulation, pos, move)
        self.counter = 0
        self.maxCount = 200 #random.randint(190,210)
        self.angle_index = 0

    def update(self):
        if self.counter == self.maxCount:
            self.reproduce()
            

            if random.random() < 0.5:
                self.pos = pygame.math.Vector2(random.randint(0,750,),random.randint(0,750))
            else:
                angle = precomputed_angles[self.angle_index]
                self.angle_index = (self.angle_index + self.id) % len(precomputed_angles)
                direction = pygame.math.Vector2(numpy.cos(angle), numpy.sin(angle))
                self.pos += 10 * direction
            
            self.counter = 0
        self.save_data("agent", "Plant")
        self.counter+=1

    def change_position(self):
        self.there_is_no_escape()
        
            
            
    

data = (
    Simulation(
        # TODO: Modify `movement_speed` and `radius` and observe the change in behaviour.
        PredatorPreyConfig(image_rotation=True, movement_speed=1, radius=50, seed=1, fps_limit=60, duration=6000)
        
    )
    
    .batch_spawn_agents(10, PredatorAgent, images=["../files/Target1.png", "../files/Target6.png"])
    .batch_spawn_agents(100, PreyAgent, images=["../files/triangle.png", "../files/Target5.png"])
    .batch_spawn_agents(100, PlantAgent, images=["../files/plant.png"])
    .run()
    .snapshots
)

summary = (
    data.filter(pl.col("frame") % 60 == 0)
        .with_columns((pl.col("frame") // 60).alias("second"))
        .group_by("second")
        .agg([
            pl.col("agent").filter(pl.col("agent") == "Predator").count().alias("predator_count"),
            pl.col("agent").filter(pl.col("agent") == "Prey").count().alias("prey_count"),
        ])
        .sort("second")
)


print(summary)

import seaborn as sns
import matplotlib.pyplot as plt

sns.lineplot(summary, x='second', y='predator_count', label='Predator')
sns.lineplot(summary, x='second', y='prey_count', label='Prey')

plt.xlabel('Second')
plt.ylabel('Count')
plt.legend()
plt.show()

plt.savefig('agents.png', dpi=300)