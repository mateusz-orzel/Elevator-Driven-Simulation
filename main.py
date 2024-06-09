import pygame
from collections import defaultdict
import random as rd

pygame.init()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800


class Person:
    def __init__(self, current_floor, direction_floor, x, y, width, height, person_before = None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.current_floor = current_floor
        self.direction_floor = direction_floor
        self.person_before = person_before


    def move(self, elevator):

        if (not self.person_before and self.x > elevator.x + elevator.width + 20) or (self.person_before and self.x > self.person_before.x + self.person_before.width + 20):
            self.x -= 2

        if (self.x == elevator.x + elevator.width + 20) and (self.current_floor == elevator.current_floor):
            self.x = elevator.x

        if self.x == elevator.x:
            self.y = elevator.y + elevator.height - self.height
        
        if self.direction_floor == elevator.current_floor:
            self.x -= 2

        if self.x < elevator.x:
            self.x -= 2


    def draw(self, window):
        pygame.draw.rect(window, BLACK, (self.x, self.y, self.width, self.height))
                
        font = pygame.font.Font(None, 24)
        text = font.render(f'{self.direction_floor}', True, WHITE)
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        
        text_rect = text.get_rect(center=(center_x, center_y))
        
        window.blit(text, text_rect)

class Elevator:
    def __init__(self, x, y, width, height, total_floors = 4):
        
        self.width = width
        self.height = height
        self.floor2y = {i:WINDOW_HEIGHT - (WINDOW_HEIGHT//total_floors)*(i + 1) for i in range(total_floors)}
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
    
        
    def draw(self, window):
        pygame.draw.rect(window, RED, (self.x, self.y, self.width, self.height))


class Simulation:

    def __init__(self, total_floors = 4):
        self.window_width = WINDOW_WIDTH
        self.window_height = WINDOW_HEIGHT
        self.run = True
        self.window = pygame.display.set_mode((self.window_width, self.window_height))
        self.total_floors = total_floors
        self.floors = {i: [] for i in range(self.total_floors)}
        self.buttons = [pygame.Rect(self.window_width - 100, WINDOW_HEIGHT - self.window_height//self.total_floors - (i * (self.window_height // self.total_floors)) + 70, 60, 40) for i in range(self.total_floors)]

        self.elevator = Elevator(self.window_width//3, 500, 100, WINDOW_HEIGHT//self.total_floors - 90, self.total_floors)


    def create_people(self, floor):

        direction_floor = rd.randint(0, self.total_floors - 1)

        try:
            person = Person(floor, direction_floor, self.window_width - 150, 70 + WINDOW_HEIGHT - self.window_height//self.total_floors - (floor * (self.window_height // self.elevator.total_floors)), 20, 40, person_before=self.floors[floor][-1])
        
        except:
            person = Person(floor, direction_floor, self.window_width - 150, 70 + WINDOW_HEIGHT - self.window_height//self.total_floors - (floor * (self.window_height // self.elevator.total_floors)), 20, 40)
        
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

            self.elevator.draw(self.window)

            for floor, people in self.floors.items():
                for person in people:
                    person.move(self.elevator)
                    person.draw(self.window)
                     
            
            pygame.display.update()



if __name__ == "__main__":
    simulation = Simulation()
    simulation.main()