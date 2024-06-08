import pygame
from collections import defaultdict
import random as rd

pygame.init()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800


class Person:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def draw(self, window):
        pygame.draw.rect(window, BLACK, (self.x, self.y, self.width, self.height))


class Elevator:
    def __init__(self, x, y, width, height, total_floors = 4):
        
        self.width = width
        self.height = height
        self.floor2y = {i:600 -self.height*i for i in range(total_floors)}
        self.current_floor = 0
        self.capacity = 4

        self.x = x
        self.y = self.floor2y[self.current_floor]
 
        self.destination_floors = []
        
        self.speed = 2
        self.total_floors = total_floors
        

    def go_floor(self, floor):

        self.current_floor = floor
        self.y = self.floor2y[self.current_floor]

    def move(self):
        pass
        
    def draw(self, surface):
        pygame.draw.rect(surface, RED, (self.x, self.y, self.width, self.height))


class Simulation:

    def __init__(self, window_width = 800, window_height = 800, total_floors = 4):
        self.window_width = window_width
        self.window_height = window_height
        self.run = True
        self.window = pygame.display.set_mode((self.window_width, self.window_height))
        self.total_floors = total_floors
        self.floors = {i: [] for i in range(self.total_floors)}
        self.buttons = [pygame.Rect(self.window_width - 100, (i * (self.window_height // self.total_floors)) + 70, 60, 40) for i in range(self.total_floors)]

        self.elevator = Elevator(350, 500, 100, 200, self.total_floors)


    def create_people(self, floor):

        person = Person(600, 70 + (floor * (self.window_height // self.elevator.total_floors)), 20, 40)
        self.floors[floor].append(person)

    def draw_button(self):
        for i, btn in enumerate(self.buttons):
            pygame.draw.rect(self.window, GRAY, btn) 

            font = pygame.font.Font(None, 24)
            text = font.render(f'+', True, BLACK)
            text_rect = text.get_rect(center=btn.center)
            self.window.blit(text, text_rect)
        
    def main(self):
                            
        while self.run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False


                elif event.type == pygame.MOUSEBUTTONDOWN:

                    pos = pygame.mouse.get_pos()
                    for i, btn in enumerate(self.buttons):
                        if btn.collidepoint(pos):
                            self.create_people(i)

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_0:
                        self.elevator.go_floor(0)
                    elif event.key == pygame.K_1:
                        self.elevator.go_floor(1)
                    elif event.key == pygame.K_2:
                        self.elevator.go_floor(2)
                    elif event.key == pygame.K_3:
                        self.elevator.go_floor(3)

            
            if rd.random() < 0.01:
                random_floor = rd.randint(0, 3)
                self.elevator.go_floor(random_floor)

            self.window.fill(WHITE)

            self.draw_button()

            for floor, people in self.floors.items():
                for person in people:
                     person.draw(self.window)

            self.elevator.draw(self.window)
            pygame.display.update()



if __name__ == "__main__":
    simulation = Simulation()
    simulation.main()