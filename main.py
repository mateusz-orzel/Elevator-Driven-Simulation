import pygame
from collections import defaultdict
import random as rd
import heapq
import time
import threading
import os
import sys
import time
import numpy as np
import matplotlib.pyplot as plt

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
YELLOW = (220, 220, 0)
BLUE = (0, 0, 255)
DARK_GRAY = (150, 150, 150)

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 840

RESULTS = []
RESULTS_DICT = {}

pygame.init()
pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Wielokolejkowy model M/M/1")

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

def update_animation_index(obj):
    obj.animation_index_break += 1
    if obj.animation_index_break == 20:
        obj.animation_index = (obj.animation_index + 1) % len(walking_frames)
        obj.animation_index_break = 0

def render_text(window, text, x, y):
    font = pygame.font.Font(None, 24)
    text_surface = font.render(text, True, BLACK)
    text_rect = text_surface.get_rect(center=(x, y))
    window.blit(text_surface, text_rect)

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

        
        self.time_start = time.time()


    def move(self, elevator):

        self.get_state(elevator)
        
        if self.state == 0:
            if self.person_before == None or (self.person_before.x + self.person_before.width + 5 < self.x):
                self.x -= 1
                update_animation_index(self)

        elif self.state == 1:
            self.animation_index = 4

        elif self.state == 2:
            self.x = elevator.x + 2
            self.y = elevator.y + elevator.height - self.height

        elif self.state == 3:
            self.x -= 1
            update_animation_index(self)

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
            #self.elevator_in_time = time.time()

            heapq.heappush(elevator.floor_queue, (-1, self.direction_floor))
            self.state = 2
            elevator.num_in += 1
            elevator.open_close()

        # Jechanie windą do konkretnego piętra
        if self.direction_floor == elevator.current_floor and self.state == 2:
            self.time = round(time.time() - self.time_start, 2)
            RESULTS.append(self.time)
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

            if self.state < 2:
                render_text(window, f'{self.direction_floor}', self.x + current_frame.get_width() // 2, self.y + 10)
            else:
                render_text(window, f'Czas obsługi: {self.time:.3f}', self.x + current_frame.get_width() // 2, self.y + 10)

class Elevator:
    def __init__(self, x, y, width, height, window, total_floors = 4, capacity = 1, speed = 2):
        
        self.width = width
        self.height = height
        self.floor2y = {i:WINDOW_HEIGHT - (WINDOW_HEIGHT//total_floors)*(i+1) for i in range(total_floors)}
    
        self.current_floor = 0
        self.destination_floor = 0
        self.capacity = capacity

        self.x = x
        self.y = self.floor2y[self.current_floor]
 
        self.destination_floors = []
        
        self.speed = speed

        self.total_floors = total_floors

        self.floor_queue = []
        heapq.heapify(self.floor_queue)

        self.emergency_rate = 0.001

        self.open = False
        self.num_in = 0

        self.window = window


    def go_floor(self, target_floor):
        step = 1 if target_floor > self.current_floor else -1

        self.destination_floor = target_floor

        for next_floor in range(self.current_floor, target_floor + step, step):
            while self.y != self.floor2y[next_floor]:
                time.sleep(0.01/self.speed)
                if self.y > self.floor2y[next_floor]:
                    self.y -= 1
                else:
                    self.y += 1

            self.current_floor = next_floor

    def set_floor(self):
        calculated_floor = (self.total_floors - (self.y) / self.height - 1)
        
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


    def make_emergency(self, emegency_time = 0.2):
        
        for i  in range(100):
            text = f"{(2 - i*emegency_time)}"
            print(text)
            render_text(self.window, text, self.x, self.y)
            time.sleep(emegency_time)
                
    
        
    def draw(self):

        self.set_floor()
        self.open_close()
        pygame.draw.rect(self.window, GRAY, (self.x, 0, self.width, WINDOW_HEIGHT))
        pygame.draw.rect(self.window, DARK_GRAY, (self.x, self.y, self.width, self.height))

        if self.open:
            pygame.draw.rect(self.window, YELLOW, (self.x + 5, self.y + 5, self.width - 10, self.height - 10))
        


    def run(self):
        
        #if rd.random() < self.emergency_rate:
        #    self.make_emergency()

        while True:
            self.move()
            time.sleep(0.5)


class Menu:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.font = pygame.font.Font(None, 32)
        CENTER_X = WINDOW_WIDTH // 2
        CENTER_Y = WINDOW_HEIGHT // 2

        self.start_button_width = 200
        self.start_button_height = 50
        self.start_button_x = CENTER_X - (self.start_button_width // 2)
        self.start_button_y = CENTER_Y + 250
        self.start_button = pygame.Rect(self.start_button_x, self.start_button_y, self.start_button_width, self.start_button_height)
        self.start_button_text = self.font.render('Symuluj', True, WHITE)

        SLIDERS_X = CENTER_X - 100
        MARGIN = 75
        self.sliders = {
            'simulation_time': {
                'rect_x': SLIDERS_X,
                'rect_y': CENTER_Y + MARGIN*-2,
                'value': 0.0,
                'dragging': False,
                'integer': True,
                'min': 0,
                'max': 500,
            },
            'people_generation_freq': {
                'rect_x': SLIDERS_X,
                'rect_y': CENTER_Y + MARGIN*-1,
                'value': 1.0,
                'dragging': False,
                'integer': True,
                'min': 1,
                'max': 99
            },
            'elevator_capacity': {
                'rect_x': SLIDERS_X,
                'rect_y': CENTER_Y + MARGIN*0,
                'value': 1,
                'dragging': False,
                'integer': True,
                'min': 1,
                'max': 3
            },
            'elevator_speed': {
                'rect_x': SLIDERS_X,
                'rect_y': CENTER_Y + MARGIN*1,
                'value': 2,
                'dragging': False,
                'integer': True,
                'min': 1,
                'max': 6
            },
            'total_floors': {
                'rect_x': SLIDERS_X,
                'rect_y': CENTER_Y + MARGIN*2,
                'value': 3,
                'dragging': False,
                'integer': True,
                'min': 3,
                'max': 7
            }
        }

        self.checkbox_rect = pygame.Rect(CENTER_X - 100, CENTER_Y + 210, 20, 20)
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
                    for key, slider in self.sliders.items():
                        if self.is_slider_handle_clicked(slider, event.pos) or self.is_slider_rect_clicked(slider, event.pos):
                            if not self.checkbox_checked or key not in ['emergency_rate', 'people_generation_freq']:
                                slider['dragging'] = True
                    if self.checkbox_rect.collidepoint(event.pos):
                        self.checkbox_checked = not self.checkbox_checked

                elif event.type == pygame.MOUSEBUTTONUP:
                    for slider in self.sliders.values():
                        slider['dragging'] = False

                elif event.type == pygame.MOUSEMOTION:
                    for key, slider in self.sliders.items():
                        if slider['dragging']:
                            self.update_slider_value(slider, event.pos)

            self.draw()
            pygame.display.update()

    def is_slider_handle_clicked(self, slider, pos):
        handle_pos = slider['rect_x'] + int((slider['value'] - slider.get('min', 0)) / (slider.get('max', 1) - slider.get('min', 0)) * 200)
        return abs(pos[0] - handle_pos) <= 5 and abs(pos[1] - (slider['rect_y'] + 5)) <= 5

    def is_slider_rect_clicked(self, slider, pos):
        rect = pygame.Rect(slider['rect_x'], slider['rect_y'], 200, 10)
        return rect.collidepoint(pos)

    def update_slider_value(self, slider, pos):
        handle_pos = max(slider['rect_x'], min(pos[0], slider['rect_x'] + 200))
        slider['value'] = (handle_pos - slider['rect_x']) / 200 * (slider.get('max', 1) - slider.get('min', 0)) + slider.get('min', 0)
        if slider['integer']:
            slider['value'] = int(slider['value'])

    def start_new_simulation(self):
        simulation = Simulation(
            window=self.window,
            total_floors=self.sliders['total_floors']['value'],
            simulation_time=self.sliders['simulation_time']['value'],
            people_generation_freq=self.sliders['people_generation_freq']['value'],
            manual_mode=self.checkbox_checked,
            elevator_capacity=self.sliders['elevator_capacity']['value'],
            speed=self.sliders['elevator_speed']['value']
        )
        simulation.main()

    def draw_slider(self, slider, label):
        pygame.draw.rect(self.window, BLACK, (slider['rect_x'], slider['rect_y'], 200, 10))
        handle_pos = slider['rect_x'] + int((slider['value'] - slider.get('min', 0)) / (slider.get('max', 1) - slider.get('min', 0)) * 200)
        pygame.draw.circle(self.window, BLACK, (handle_pos, slider['rect_y'] + 5), 7)
        display_value = f'{slider["value"]:.3f}' if not slider['integer'] else f'{slider["value"]:.0f}'
        text = self.font.render(f'{label}: {display_value}', True, DARK_GRAY)
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, slider['rect_y'] + 30))
        self.window.blit(text, text_rect)

    def draw(self):
        self.window.fill(WHITE)

        text = self.font.render('Parametry', True, DARK_GRAY)
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 200))
        self.window.blit(text, text_rect)

        pygame.draw.rect(self.window, DARK_GRAY, self.start_button)
        start_button_text_rect = self.start_button_text.get_rect(center=self.start_button.center)
        self.window.blit(self.start_button_text, start_button_text_rect)

        self.draw_slider(self.sliders['simulation_time'], 'Czas Symulacji')
        self.draw_slider(self.sliders['people_generation_freq'], 'Częstotliwość Generowania Klientów')
        self.draw_slider(self.sliders['elevator_capacity'], 'Pojemność Windy')
        self.draw_slider(self.sliders['elevator_speed'], 'Szybkość Windy')
        self.draw_slider(self.sliders['total_floors'], 'Liczba Pięter')

        pygame.draw.rect(self.window, BLACK, self.checkbox_rect, 2)
        if self.checkbox_checked:
            pygame.draw.line(self.window, BLACK, (self.checkbox_rect.left + 4, self.checkbox_rect.centery), (self.checkbox_rect.centerx, self.checkbox_rect.bottom - 4), 2)
            pygame.draw.line(self.window, BLACK, (self.checkbox_rect.centerx, self.checkbox_rect.bottom - 4), (self.checkbox_rect.right - 4, self.checkbox_rect.top + 4), 2)

        checkbox_label = self.font.render('Manualne Dodawanie Ludzi', True, DARK_GRAY)
        checkbox_label_rect = checkbox_label.get_rect(midleft=(self.checkbox_rect.right + 10, self.checkbox_rect.centery))
        self.window.blit(checkbox_label, checkbox_label_rect)

        pygame.display.flip()

class Simulation:

    def __init__(self, window, simulation_time, people_generation_freq, manual_mode, elevator_capacity, total_floors = 4, speed = 2):

        self.total_floors = total_floors
        #self.emergency_rate = emergency_rate
        self.people_generation_freq = people_generation_freq
        self.manual_mode = manual_mode
        self.elevator_capacity = elevator_capacity

        self.run = True
        self.window = window
        self.floors = {i: [] for i in range(self.total_floors)}
        self.buttons = [pygame.Rect(WINDOW_WIDTH - 100, WINDOW_HEIGHT - int(0.5*(WINDOW_HEIGHT//self.total_floors)) - 20 - (i * (WINDOW_HEIGHT // self.total_floors)), 40, 40) for i in range(self.total_floors)]

        self.elevator = Elevator(WINDOW_WIDTH - 700, 500, 100, WINDOW_HEIGHT//self.total_floors, window, self.total_floors, capacity=self.elevator_capacity, speed=speed)

        self.elevator_thread = threading.Thread(target=self.elevator.run)
        self.elevator_thread.daemon = True
        self.elevator_thread.start()
        
        self.last_people_generation_time = time.time()

        self.back_button_width = 160
        self.back_button_height = 40
        self.back_button = pygame.Rect(10, WINDOW_HEIGHT - self.back_button_height - 10, self.back_button_width, self.back_button_height)
        self.back_button_text = pygame.font.Font(None, 32).render('Wróć do Menu', True, WHITE)
        self.start_timer = time.time()
        self.simulation_time = simulation_time
        self.run_stats_time = False

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

    def draw_back_button(self):
        pygame.draw.rect(self.window, DARK_GRAY, self.back_button)
        back_button_text_rect = self.back_button_text.get_rect(center=self.back_button.center)
        self.window.blit(self.back_button_text, back_button_text_rect)

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
            text = font.render(f'Piętro {i}', True, BLACK)
            self.window.blit(text, (10, y + 5))

    def take_stats(self, moving_mean_window_size = 5):
        data = np.array(RESULTS)
        mean = np.mean(data)
        std = np.std(data)
        
        window_size = moving_mean_window_size
        moving_mean = np.convolve(data, np.ones(window_size)/window_size, mode='valid')
        random_time = rd.choice(RESULTS[int(0.2*len(RESULTS)):])

        self.mean = mean
        self.std = std
        self.random_time = random_time
        self.moving_mean = moving_mean


    def display_statistics(self):
        if not RESULTS:
            return
        
        font = pygame.font.Font(None, 40)

        mean_text = font.render(f"Średnia: {self.mean:.2f}", True, BLACK)
        std_text = font.render(f"Odchylenie Standardowe: {self.std:.2f}", True, BLACK)
        random_person_handling_time = font.render(f"Czas Obsługi Pojedynczej Losowej Osoby: {self.random_time}", True, BLACK)


        plt.figure()
        plt.plot(self.moving_mean, label="Średnia Ruchoma")
        plt.xlabel("Próba")
        plt.ylabel("Wartość")
        plt.title("Wykres Średniej Ruchomej")
        plt.legend()
        plt.savefig('moving_mean_plot.png')
        plt.close()

        plot_image = pygame.image.load('moving_mean_plot.png')
        plot_rect = plot_image.get_rect()
        plot_rect.topleft = (10, 50)
        self.window.blit(plot_image, plot_rect)

        self.window.blit(mean_text, (10, 550))
        self.window.blit(std_text, (10, 580))
        self.window.blit(random_person_handling_time, (10, 610))

    def main(self):
                            
        while self.run:

            RESULTS = []

            if time.time() - self.start_timer > self.simulation_time:
                self.run_stats_time = True
                break

            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN and self.manual_mode:

                    pos = pygame.mouse.get_pos()
                    for i, btn in enumerate(self.buttons):
                        if btn.collidepoint(pos):
                            self.create_people(i)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.back_button.collidepoint(event.pos):
                        self.run = False
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)


            if self.back_button.collidepoint(pygame.mouse.get_pos()):
                mouse_hovering = True
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

            self.window.fill(WHITE)

            if not self.manual_mode:
                self.generate_people()

            self.draw_floors()
            self.draw_button(self.manual_mode)
            self.draw_back_button()

            self.elevator.draw()

            for floor, people in self.floors.items():
                for person in people:

                    if person.to_delete:
                        person.to_delete = False
                        self.floors[floor].pop(0)
                        
                    person.move(self.elevator)
                    person.draw(self.window)
                     
            
            pygame.display.update()

        #print(RESULTS)

        if self.run_stats_time:
            self.take_stats()

        while self.run_stats_time:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.back_button.collidepoint(event.pos):
                        self.run_stats_time = False
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

            if self.back_button.collidepoint(pygame.mouse.get_pos()):
                mouse_hovering = True
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

            self.window.fill(WHITE)
            self.display_statistics()
            self.draw_back_button()
            pygame.display.update()


if __name__ == "__main__":
    menu = Menu()
    menu.main()