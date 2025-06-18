from dataclasses import dataclass

from vi import Agent, Config, Simulation
from pygame.math import Vector2
import random
<<<<<<< HEAD
#import polars as pl
#import seaborn as sns
import pygame
import numpy

seed = 2
random.seed(seed)

precomputed_angles = [random.uniform(0, 2 * numpy.pi) for _ in range(1000)]


#countList = [[],[]]

def calc_LJ_force(distance, epsilon=100, sigma=0.01):
    if distance == 0:
        return 0  # Avoid division by zero
    return 24 * epsilon * (2 * (sigma / distance)**13 - (sigma / distance)**7)


@dataclass
class PredatorPreyConfig(Config):
    prey_speed = 1
    predator_speed = 1
    pass


class PredatorAgent(Agent[PredatorPreyConfig]):
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
                    #print("plant")
                    self.food += 75
                    other[0].kill()
                    if self.food >= 150:
                        self.food -= 50
                        self.reproduce()

        if self.food <= 0:
            self.kill()

        self.food -= 0.3
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
        

class PreyAgent(Agent[PredatorPreyConfig]):
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
                    self.food += 15
                    if self.food >= 150:
                        self.food -= 50
                        self.reproduce()
                    other[0].kill()

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
      
class PlantAgent(Agent[PredatorPreyConfig]):
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

        self.counter+=1

    def change_position(self):
        pass
        
            
            
    

(
    Simulation(
        # TODO: Modify `movement_speed` and `radius` and observe the change in behaviour.
        PredatorPreyConfig(image_rotation=True, movement_speed=1, radius=50, seed=seed, fps_limit=60, ), #duration=10 *60 
         
    )
    
    .batch_spawn_agents(10, PredatorAgent, images=["images/Target1.png", "images/Target6.png"])
    .batch_spawn_agents(100, PreyAgent, images=["images/triangle.png", "images/Target5.png"])
    .batch_spawn_agents(100, PlantAgent, images=["images/plant.png"])
    .run()
)

#countDataFrame = pl.DataFrame(countList)
#print(countDataFrame)

#plot = sns.relplot(countDataFrame, x=countDataFrame['column_0'], y=countDataFrame['column_1'])
#plot.savefig('agents.png', dpi=300)