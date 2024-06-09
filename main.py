import pygame
from collections import defaultdict
import random as rd
import heapq
import time
import threading


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
        self.state = 0


    def move(self, elevator):

        self.get_state(elevator)
        
        if self.state == 0:
            self.x -= 2

        elif self.state == 1:
            pass

        elif self.state == 2:
            self.x = elevator.x + 2
            self.y = elevator.y + elevator.height - self.height - 2

        elif self.state == 3:
            self.x -= 2


    def get_state(self, elevator):

        if self.x > elevator.x + elevator.width + 20:
            self.state = 0

        if self.x == elevator.x + elevator.width + 20 and self.state != 1:
            heapq.heappush(elevator.floor_queue, (self.current_floor, self.direction_floor))
            self.state  = 1

        elif self.current_floor == elevator.current_floor:
            self.state = 2

        elif self.direction_floor == elevator.current_floor:
            self.state = 3


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

        self.floor_queue = []
        heapq.heapify(self.floor_queue)

        self.emergency_rate = 0.001
        

    def go_floor(self, target_floor):

        step = 1 if target_floor > self.current_floor else -1

        for next_floor in range(self.current_floor + step, target_floor + step, step):

            while self.y != self.floor2y[self.current_floor]:
                time.sleep(0.01)  
                if self.y > self.floor2y[self.current_floor]:
                    self.y -= 1 
                else:
                    self.y += 1 

            self.current_floor = next_floor

    def move(self):
        
        if self.floor_queue:
            floor, dest = heapq.heappop(self.floor_queue)
            self.go_floor(floor)
            time.sleep(1)
            self.go_floor(dest)
    
        
    def draw(self, window):
        pygame.draw.rect(window, RED, (self.x, self.y, self.width, self.height))

    def run(self):
        while True:
            self.move()
            time.sleep(1)

class Simulation:

    def __init__(self, total_floors = 4):
        self.window_width = WINDOW_WIDTH
        self.window_height = WINDOW_HEIGHT
        self.run = True
        self.window = pygame.display.set_mode((self.window_width, self.window_height))
        self.total_floors = total_floors
        self.floors = {i: [] for i in range(self.total_floors)}
        self.buttons = [pygame.Rect(self.window_width - 100, WINDOW_HEIGHT - self.window_height//self.total_floors - (i * (self.window_height // self.total_floors)) + 70, 60, 40) for i in range(self.total_floors)]

        self.elevator = Elevator(self.window_width//3, 500, 100, WINDOW_HEIGHT//self.total_floors, self.total_floors)

        self.elevator_thread = threading.Thread(target=self.elevator.run)
        self.elevator_thread.daemon = True
        self.elevator_thread.start()


    def create_people(self, floor):
        
        direction_floor = rd.randint(0, self.total_floors - 1)

        while direction_floor == floor:
            direction_floor = rd.randint(0, self.total_floors - 1)

        try:
            person = Person(floor, direction_floor, self.window_width - 150, 70 + WINDOW_HEIGHT - self.window_height//self.total_floors - (floor * (self.window_height // self.elevator.total_floors)), 15, 40, person_before=self.floors[floor][-1])
        
        except:
            person = Person(floor, direction_floor, self.window_width - 150, 70 + WINDOW_HEIGHT - self.window_height//self.total_floors - (floor * (self.window_height // self.elevator.total_floors)), 15, 40)
        
        self.floors[floor].append(person)


    def draw_button(self):
        for i, btn in enumerate(self.buttons):
            pygame.draw.rect(self.window, GRAY, btn) 

            font = pygame.font.Font(None, 24)
            text = font.render(f'+', True, BLACK)
            text_rect = text.get_rect(center=btn.center)
            self.window.blit(text, text_rect)


    def draw_floors(self):
        floor_height = self.window_height // self.total_floors

        for i in range(self.total_floors):
            y = self.window_height - (i + 1) * floor_height

            pygame.draw.line(self.window, BLACK, (0, y), (self.window_width, y), 2)

            font = pygame.font.Font(None, 36)
            text = font.render(f'Floor {i}', True, BLACK)
            self.window.blit(text, (10, y + 5))

    def main(self):
                            
        while self.run:
            
            print(self.elevator.floor_queue)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False

                elif event.type == pygame.MOUSEBUTTONDOWN:

                    pos = pygame.mouse.get_pos()
                    for i, btn in enumerate(self.buttons):
                        if btn.collidepoint(pos):
                            self.create_people(i)

            self.window.fill(WHITE)

            self.draw_floors()
            self.draw_button()
            
            #self.elevator.move()

            self.elevator.draw(self.window)

            for floor, people in self.floors.items():
                for person in people:
                    person.move(self.elevator)
                    person.draw(self.window)
                     
            
            pygame.display.update()


if __name__ == "__main__":
    simulation = Simulation(total_floors=7)
    simulation.main()