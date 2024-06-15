import pygame
from collections import defaultdict
import random as rd
import heapq
import time
import threading
import os
import sys
import time

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
YELLOW = (220, 220, 0)
BLUE = (0, 0, 255)
DARK_GRAY = (150, 150, 150)

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

pygame.init()
pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

num_frames = 6

walking_frames = []

frames_directory = './images'

for i in range(1, num_frames + 1):
    frame_path = os.path.join(frames_directory, f'frame_{i}.png')
    

    if os.path.exists(frame_path):
        frame = pygame.image.load(frame_path).convert_alpha()
        color_key = frame.get_at((0, 0))  # Gets the color of the upper left corner
        frame.set_colorkey(color_key) 
        frame = pygame.transform.flip(frame, True, False)
        walking_frames.append(frame)

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
        self.to_delete = False
        self.animation_index = 0
        self.animation_index_break = 0
        self.priority = False


    def move(self, elevator):

        self.get_state(elevator)
        
        if self.state == 0:
            if self.person_before == None or (self.person_before.x + self.person_before.width + 5 < self.x):
                self.x -= 1
                self.animation_index_break += 1
                if self.animation_index_break == 20:
                    self.animation_index = (self.animation_index + 1) % len(walking_frames)
                    self.animation_index_break = 0

        elif self.state == 1:
            self.animation_index = 4

        elif self.state == 2:
            self.x = elevator.x + 2
            self.y = elevator.y + elevator.height - self.height

        elif self.state == 3:
            self.x -= 1
            self.animation_index_break += 1
            if self.animation_index_break == 20:
                self.animation_index = (self.animation_index + 1) % len(walking_frames)
                self.animation_index_break = 0

        elif self.state == 4:
            self.to_delete = True


    def get_state(self, elevator):

        # Biegnięcie w kierunku windy
        if self.x > elevator.x + elevator.width + 20:
            self.state = 0

        # Zawołanie windy
        if self.x == elevator.x + elevator.width + 20 and self.state == 0:
            heapq.heappush(elevator.floor_queue, (0, self.current_floor))
            self.state  = 1
        
        # Wsiadanie do windy
        if self.current_floor == elevator.current_floor and self.state == 1 and elevator.open:
            heapq.heappush(elevator.floor_queue, (-1, self.direction_floor))
            self.state = 2
            elevator.num_in += 1
            elevator.open_close()

        # Jechanie windą do konkretnego piętra
        if self.direction_floor == elevator.current_floor and self.state == 2:
            self.state = 3
            elevator.num_in -= 1
            elevator.open_close()

        # Usuwanie obiektu po przejściu do galerii
        if self.x < 0 and self.state == 3:
            self.state = 4


    def draw(self, window):

        if self.state != 2:
            current_frame = walking_frames[self.animation_index]
            window.blit(current_frame, (self.x, self.y))

            font = pygame.font.Font(None, 24)
            text = font.render(f'{self.direction_floor}', True, BLACK)

            text_x = self.x + current_frame.get_width() // 2
            text_y = self.y

            text_rect = text.get_rect(center=(text_x, text_y))

            window.blit(text, text_rect)

class Elevator:
    def __init__(self, x, y, width, height, total_floors = 4):
        
        self.width = width
        self.height = height
        self.floor2y = {i:WINDOW_HEIGHT - (WINDOW_HEIGHT//total_floors)*(i+1) for i in range(total_floors)}
    
        self.current_floor = 0
        self.destination_floor = 0
        self.capacity = 2

        self.x = x
        self.y = self.floor2y[self.current_floor]
 
        self.destination_floors = []
        
        self.speed = 2
        self.total_floors = total_floors

        self.floor_queue = []
        heapq.heapify(self.floor_queue)

        self.emergency_rate = 0.001

        self.open = False
        self.num_in = 0


    def go_floor(self, target_floor):
        step = 1 if target_floor > self.current_floor else -1

        self.destination_floor = target_floor

        for next_floor in range(self.current_floor, target_floor + step, step):
            while self.y != self.floor2y[next_floor]:
                time.sleep(0.01)
                if self.y > self.floor2y[next_floor]:
                    self.y -= 1
                else:
                    self.y += 1

            self.current_floor = next_floor

    def set_floor(self):
        calculated_floor = (self.total_floors - (self.y - 2) / self.height - 1)
        
        if calculated_floor.is_integer():
            self.current_floor = int(calculated_floor)
        else:
            self.current_floor = calculated_floor
        

    def open_close(self):
        if self.destination_floor == self.current_floor and self.num_in < self.capacity:
            self.open = True

        else:
            self.open = False

    def move(self):
        
        if self.floor_queue:
            _, dest = heapq.heappop(self.floor_queue)
            self.go_floor(dest)

    def make_awaria(self):
        if rd.random() < self.emergency_rate:
            print()
    
        
    def draw(self, window):
        
        self.set_floor()
        self.open_close()
        pygame.draw.rect(window, GRAY, (self.x, 0, self.width, WINDOW_HEIGHT))
        pygame.draw.rect(window, DARK_GRAY, (self.x, self.y, self.width, self.height))

        if self.open:
            pygame.draw.rect(window, YELLOW, (self.x + 5, self.y + 5, self.width - 10, self.height - 10))
            

    def run(self):
        while True:
            self.move()
            time.sleep(1)


class Menu:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.font = pygame.font.Font(None, 32)
        
        self.start_button_width = 200
        self.start_button_height = 50
        self.start_button_x = (WINDOW_WIDTH // 2) - (self.start_button_width // 2)
        self.start_button_y = (WINDOW_HEIGHT // 2) + 250
        self.start_button = pygame.Rect(self.start_button_x, self.start_button_y, self.start_button_width, self.start_button_height)
        self.start_button_text = self.font.render('Start Simulation', True, WHITE)

        self.slider_rect_width = 200
        self.slider_rect_x = (WINDOW_WIDTH // 2) - (self.slider_rect_width // 2)
        self.slider_rect_y = (WINDOW_HEIGHT // 2) - 50
        self.slider_rect = pygame.Rect(self.slider_rect_x, self.slider_rect_y, self.slider_rect_width, 10)
        self.slider_handle_pos = self.slider_rect_x
        self.slider_dragging = False
        self.emergency_rate = 0.0

        self.freq_slider_rect_x = (WINDOW_WIDTH // 2) - (self.slider_rect_width // 2)
        self.freq_slider_rect_y = (WINDOW_HEIGHT // 2) + 50
        self.freq_slider_rect = pygame.Rect(self.freq_slider_rect_x , self.freq_slider_rect_y, self.slider_rect_width, 10)
        self.freq_slider_handle_pos = self.freq_slider_rect_x 
        self.freq_slider_dragging = False
        self.people_generation_freq = 1.0 

        self.checkbox_rect = pygame.Rect(WINDOW_WIDTH // 2 - 100, (WINDOW_HEIGHT // 2) + 150, 20, 20)
        self.checkbox_checked = False

    def main(self):
        self.draw()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.start_button.collidepoint(event.pos):
                        self.start_new_simulation()
                    elif self.slider_rect.collidepoint(event.pos) or abs(event.pos[0] - self.slider_handle_pos) <= 5:
                        if not self.checkbox_checked:
                            self.slider_dragging = True
                    elif self.freq_slider_rect.collidepoint(event.pos) or abs(event.pos[0] - self.freq_slider_handle_pos) <= 5:
                        if not self.checkbox_checked:
                            self.freq_slider_dragging = True
                    elif self.checkbox_rect.collidepoint(event.pos):
                        self.checkbox_checked = not self.checkbox_checked

                elif event.type == pygame.MOUSEBUTTONUP:
                    self.slider_dragging = False
                    self.freq_slider_dragging = False

                elif event.type == pygame.MOUSEMOTION:
                    if self.slider_dragging:
                        self.slider_handle_pos = max(self.slider_rect_x, min(event.pos[0], self.slider_rect_x + self.slider_rect_width))
                        self.emergency_rate = (self.slider_handle_pos - self.slider_rect_x) / self.slider_rect_width
                    elif self.freq_slider_dragging:
                        self.freq_slider_handle_pos = max(self.freq_slider_rect_x, min(event.pos[0], self.freq_slider_rect_x + self.slider_rect_width))
                        self.people_generation_freq = int(1 + (self.freq_slider_handle_pos - self.freq_slider_rect_x) / self.slider_rect_width * 98)

            self.draw()
            pygame.display.update()

    def start_new_simulation(self):
        simulation = Simulation(window=self.window, total_floors=6, emergency_rate=self.emergency_rate, people_generation_freq=self.people_generation_freq, manual_mode=self.checkbox_checked)
        simulation.main()

    def draw(self):
        self.window.fill(WHITE)

        text = self.font.render('Parameters', True, DARK_GRAY)
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100))
        self.window.blit(text, text_rect)

        pygame.draw.rect(self.window, DARK_GRAY, self.start_button)
        start_button_text_rect = self.start_button_text.get_rect(center=self.start_button.center)
        self.window.blit(self.start_button_text, start_button_text_rect)

        pygame.draw.rect(self.window, BLACK, self.slider_rect)
        pygame.draw.circle(self.window, BLACK, (self.slider_handle_pos, self.slider_rect_y + 5), 7)
        rate_text = self.font.render(f'Emergency Rate: {self.emergency_rate:.3f}', True, DARK_GRAY)
        rate_text_rect = rate_text.get_rect(center=(WINDOW_WIDTH // 2, self.slider_rect_y + 30))
        self.window.blit(rate_text, rate_text_rect)

        slider_color = DARK_GRAY if self.checkbox_checked else BLACK
        pygame.draw.rect(self.window, slider_color, self.freq_slider_rect)
        pygame.draw.circle(self.window, slider_color, (self.freq_slider_handle_pos, self.freq_slider_rect_y + 5), 7)
        freq_text = self.font.render(f'People Generation Freq: {self.people_generation_freq:.1f}', True, slider_color)
        freq_text_rect = freq_text.get_rect(center=(WINDOW_WIDTH // 2, self.freq_slider_rect_y + 30))
        self.window.blit(freq_text, freq_text_rect)

        pygame.draw.rect(self.window, BLACK, self.checkbox_rect, 2)
        if self.checkbox_checked:
            pygame.draw.line(self.window, BLACK, (self.checkbox_rect.left + 4, self.checkbox_rect.centery), (self.checkbox_rect.centerx, self.checkbox_rect.bottom - 4), 2)
            pygame.draw.line(self.window, BLACK, (self.checkbox_rect.centerx, self.checkbox_rect.bottom - 4), (self.checkbox_rect.right - 4, self.checkbox_rect.top + 4), 2)

        checkbox_label = self.font.render('Manual Adding People', True, DARK_GRAY)
        checkbox_label_rect = checkbox_label.get_rect(midleft=(self.checkbox_rect.right + 10, self.checkbox_rect.centery))
        self.window.blit(checkbox_label, checkbox_label_rect)

        pygame.display.flip()


class Simulation:

    def __init__(self, window, emergency_rate, people_generation_freq, manual_mode, total_floors = 4):


        self.total_floors = total_floors
        self.emergency_rate = emergency_rate
        self.people_generation_freq = people_generation_freq
        self.manual_mode = manual_mode


        self.run = True
        self.window = window
        self.total_floors = total_floors
        self.floors = {i: [] for i in range(self.total_floors)}
        self.buttons = [pygame.Rect(WINDOW_WIDTH - 100, WINDOW_HEIGHT - int(0.5*(WINDOW_HEIGHT//self.total_floors)) - 20 - (i * (WINDOW_HEIGHT // self.total_floors)), 40, 40) for i in range(self.total_floors)]

        self.elevator = Elevator(WINDOW_WIDTH - 700, 500, 100, WINDOW_HEIGHT//self.total_floors, self.total_floors)

        self.elevator_thread = threading.Thread(target=self.elevator.run)
        self.elevator_thread.daemon = True
        self.elevator_thread.start()\
        

        self.last_people_generation_time = time.time()

    def generate_people(self):

        time_now = time.time()

        if time_now - self.last_people_generation_time > (60/self.people_generation_freq):

            floor = rd.randint(0, self.total_floors - 1)
            self.create_people(floor)

            self.last_people_generation_time = time_now
                

    def create_people(self, floor):
        
        direction_floor = rd.randint(0, self.total_floors - 1)

        people_width = walking_frames[0].get_width()
        people_height = walking_frames[0].get_height()

        while direction_floor == floor:
            direction_floor = rd.randint(0, self.total_floors - 1)

        try:
            person = Person(floor, direction_floor, WINDOW_WIDTH - 150, WINDOW_HEIGHT - WINDOW_HEIGHT//self.total_floors - ((floor - 1) * (WINDOW_HEIGHT // self.elevator.total_floors)) - people_height, people_width, people_height, person_before=self.floors[floor][-1])
        
        except:
            person = Person(floor, direction_floor, WINDOW_WIDTH - 150, WINDOW_HEIGHT - WINDOW_HEIGHT//self.total_floors - ((floor - 1) * (WINDOW_HEIGHT // self.elevator.total_floors)) - people_height, people_width, people_height)
        
        self.floors[floor].append(person)


    def draw_button(self, mode):

        if mode:
            for i, btn in enumerate(self.buttons):
                pygame.draw.rect(self.window, GRAY, btn) 

                font = pygame.font.Font(None, 65)
                text = font.render(f'+', True, BLACK)
                text_rect = text.get_rect(center=(btn.centerx, btn.centery))
                text_rect.y -= 3
                
                self.window.blit(text, text_rect)


    def draw_floors(self):
        floor_height = WINDOW_HEIGHT // self.total_floors

        for i in range(self.total_floors):
            y = WINDOW_HEIGHT - (i + 1) * floor_height

            pygame.draw.line(self.window, BLACK, (0, y), (WINDOW_WIDTH, y), 2)

            font = pygame.font.Font(None, 36)
            text = font.render(f'Floor {i}', True, BLACK)
            self.window.blit(text, (10, y + 5))


    def main(self):
                            
        while self.run:
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN and self.manual_mode:

                    pos = pygame.mouse.get_pos()
                    for i, btn in enumerate(self.buttons):
                        if btn.collidepoint(pos):
                            self.create_people(i)

            self.window.fill(WHITE)

            if not self.manual_mode:
                self.generate_people()

            self.draw_floors()
            self.draw_button(self.manual_mode)

            self.elevator.draw(self.window)

            for floor, people in self.floors.items():
                for person in people:

                    if person.to_delete:
                        person.to_delete = False
                        self.floors[floor].pop(0)
                        
                    person.move(self.elevator)
                    person.draw(self.window)
                     
            
            pygame.display.update()


if __name__ == "__main__":
    menu = Menu()
    menu.main()