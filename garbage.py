import pygame
import sys
from pygame.math import Vector2
from collections import namedtuple
from enum import Enum
import random
import numpy as np


pygame.mixer.pre_init(44100,-16,2,512)
pygame.init()
cell_size =40 
cell_number = 20


screen = pygame.display.set_mode((cell_number*cell_size,cell_number*cell_size))
clock = pygame.time.Clock()
SCREEN_UPDATE = pygame.USEREVENT
pygame.time.set_timer(SCREEN_UPDATE,150)

#reset
#reward
#game_iteration
#is_collision
class Direction(Enum):
    RIGHT =Vector2(1,0)
    LEFT=Vector2(-1,0)
    UP=Vector2(0,-1)
    DOWN=Vector2(0,1)

Point = namedtuple('Point', 'x, y')

class Garbage:
    def __init__(self):
        self.randomize()
        
        self.apple = pygame.image.load('img/garbage.png').convert_alpha()  

    def draw_garbage(self):
        #create rectangle
        garbage_rect = pygame.Rect(self.pos.x*cell_size,self.pos.y*cell_size,cell_size,cell_size)
        screen.blit(self.apple,garbage_rect)
        # pygame.draw.rect(screen,(126,166,114),garbage_rect)
    def randomize(self):
        self.x = random.randint(0,cell_number -1)
        self.y = random.randint(0,cell_number -1)
        self.pos = Vector2(self.x,self.y)

class SnakeAI:
    def __init__(self):
        self.body = [Vector2(5,10),Vector2(4,10),Vector2(3,10)]
        self.direction = Vector2(1,0)
        self.new_block = False
        self.frame_iteration = 0
        self.score = 0

        self.head_up = pygame.image.load('img/truck_head_up.png').convert_alpha()
        self.head_down = pygame.image.load('img/truck_head_down.png').convert_alpha()
        self.head_right = pygame.image.load('img/truck_head_right.png').convert_alpha()
        self.head_left = pygame.image.load('img/truck_head_left.png').convert_alpha()
        
        self.tail_up = pygame.image.load('img/truck_tail_up.png').convert_alpha()
        self.tail_down = pygame.image.load('img/truck_tail_down.png').convert_alpha()
        self.tail_right = pygame.image.load('img/truck_tail_right.png').convert_alpha()
        self.tail_left = pygame.image.load('img/truck_tail_left.png').convert_alpha()
        
        self.body_vertical = pygame.image.load('img/truck_body_vertical.png').convert_alpha()
        self.body_horizontal = pygame.image.load('img/truck_body_horizontal.png').convert_alpha()
        
        self.body_tr = pygame.image.load('img/truck_body_tr.png').convert_alpha()
        self.body_tl = pygame.image.load('img/truck_body_tl.png').convert_alpha()
        self.body_br = pygame.image.load('img/truck_body_br.png').convert_alpha()
        self.body_bl = pygame.image.load('img/truck_body_bl.png').convert_alpha()

        self.crunch_sound = pygame.mixer.Sound('Sound/crunch.wav')

    def draw_snake(self):
        self.update_head_graphics()
        self.update_tail_graphics()
        for index,block in enumerate(self.body):
            x_pos = block.x *cell_size
            y_pos = block.y * cell_size
            block_rect = pygame.Rect(x_pos,y_pos,cell_size,cell_size)

            if index == 0:
                screen.blit(self.head,block_rect)
            elif index == len(self.body)-1:
                screen.blit(self.tail, block_rect)
            else:
                previous_block = self.body[index +1] - block
                next_block = self.body[index-1]-block
                if previous_block.x == next_block.x:
                    screen.blit(self.body_vertical,block_rect)
                elif previous_block.y == next_block.y:
                    screen.blit(self.body_horizontal,block_rect)
                else:
                    if previous_block.x == -1 and next_block.y == -1 or previous_block.y == -1 and next_block.x == -1:
                        screen.blit(self.body_tl,block_rect) 
                    elif previous_block.x == -1 and next_block.y == 1 or previous_block.y == 1 and next_block.x == -1:
                        screen.blit(self.body_bl,block_rect)
                    elif previous_block.x == 1 and next_block.y == -1 or previous_block.y == -1 and next_block.x == 1:
                        screen.blit(self.body_tr,block_rect)
                    elif previous_block.x == 1 and next_block.y == 1 or previous_block.y == 1 and next_block.x == 1:
                        screen.blit(self.body_br, block_rect)
            
    def update_tail_graphics(self):
        tail_relation = self.body[-2] - self.body[-1]
        if tail_relation == Vector2(1,0):
            self.tail = self.tail_left
        elif tail_relation == Vector2(-1,0):
            self.tail = self.tail_right
        elif tail_relation == Vector2(0,-1):
            self.tail = self.tail_down
        elif tail_relation == Vector2(0,1):
            self.tail = self.tail_up

    def update_head_graphics(self):
        head_relation = self.body[1] - self.body[0]
        if head_relation == Vector2(1,0):
            self.head = self.head_left
        elif head_relation == Vector2(-1,0):
            self.head = self.head_right
        elif head_relation == Vector2(0,-1):
            self.head = self.head_down
        elif head_relation == Vector2(0,1):
            self.head = self.head_up

    def move_snake(self, action):
        if self.new_block == True:
            body_copy = self.body[:]
            body_copy.insert(0,body_copy[0]+ self.direction)
            self.body = body_copy
            self.new_block = False
        else:
            body_copy = self.body[:-1]
            body_copy.insert(0,body_copy[0]+ self.direction)
            self.body = body_copy

    def play_crunch_sound(self):
        self.crunch_sound.play()

    def add_block(self):
        self.new_block = True

    def reset(self):
        self.body = [Vector2(5,10),Vector2(4,10),Vector2(3,10),Vector2(2,10)]
        self.direction = Vector2(1,0)
        self.score = 0
        

class main:
    def __init__(self):
        self.snake= SnakeAI()
        self.garbage = Garbage()
        self.reward =0
        
        self.alive = True
        #well
        
        self.game_font = pygame.font.Font('Font/PoetsenOne-Regular.ttf',25)

        
    
    def update(self,action):
        self.snake.move_snake(action)
        self.check_collision()
        if self.snake.frame_iteration > 100*(self.snake.score+3):
            self.reward = -10
        
    def draw_elements(self):
        self.draw_grass()
        self.garbage.draw_garbage()
        self.snake.draw_snake()
        self.draw_score()
    
    def check_collision(self):
        if self.garbage.pos == self.snake.body[0]:
            self.garbage.randomize()
            # self.snake.add_block()
            self.snake.play_crunch_sound()
            self.snake.score +=1
            self.reward = 10
        for block in self.snake.body[1:]:
            if block == self.garbage.pos:
                self.garbage.randomize()
            

    def play_step(self, action):
        self.snake.frame_iteration += 1
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
          #draw all the elements
        clock_wise = [Vector2(1,0),Vector2(0,1),Vector2(-1,0),Vector2(0,-1)]
        idx = clock_wise.index(self.snake.direction)

        if np.array_equal(action, [1,0,0]):
            new_dir = clock_wise[idx]
        elif np.array_equal(action, [0,1,0]):
            next_idx = (idx+1)%4
            new_dir = clock_wise[next_idx]
        else:
            next_idx = (idx -1)%4
            new_dir = clock_wise[next_idx]
        self.snake.direction = new_dir

        self.reward = 0
        # pygame.time.delay(150)
        self.update(action)
        if self.check_fail()== True:
            self.reward = -10
            self.alive = False

        screen.fill((192,192,192))
        self.draw_elements()
        pygame.display.update()
        clock.tick(60)
        return self.reward,self.alive,self.snake.score
    
    def draw_score(self):
        score_text = str(self.snake.score)
        score_surface = self.game_font.render(score_text,True,(56,74,12))
        score_x = cell_number* cell_size - 60
        score_y = cell_number*cell_size - 40
        score_rect = score_surface.get_rect(center = (score_x,score_y)) 
        apple_rect = self.garbage.apple.get_rect(midright = (score_rect.left, score_rect.centery))
        bg_rect = pygame.Rect(apple_rect.left,apple_rect.top,apple_rect.width+score_rect.width+ 10,apple_rect.height)

        pygame.draw.rect(screen,(167,209,61),bg_rect)
        screen.blit(score_surface,score_rect)
        screen.blit(self.garbage.apple,apple_rect)
        pygame.draw.rect(screen, (56,74,12),bg_rect,2)

    def check_fail(self, pt = None):
        if pt is None:
            pt = self.snake.body[0]

        if not 0 <= pt.x < cell_number or not 0 <= pt.y < cell_number:
            return True
        if pt in self.snake.body[1:]:
            return True
        return False
    
    def draw_grass(self):
        grass_colour=(169,169,169)
        for row in range(cell_number):
            if row%2 == 0:     
                for col in range(cell_number):
                    if col%2 == 0:
                        grass_rect = pygame.Rect(col*cell_size,row*cell_size,cell_size,cell_size)
                        pygame.draw.rect(screen,grass_colour,grass_rect)
            else:
                for col in range(cell_number):
                    if col%2 != 0:
                        grass_rect = pygame.Rect(col*cell_size,row*cell_size,cell_size,cell_size)
                        pygame.draw.rect(screen,grass_colour,grass_rect)
            
    def game_over(self):
        self.alive = True
        self.snake.frame_iteration = 0
        self.reward = 0
        self.snake.reset()


    def run(self,action):
        while True:
            self.play_step(action)  
            screen.fill((192,192,192))
            self.draw_elements()
            pygame.display.update()
            clock.tick(60)


# game = main()
# game.run([1,0,0])

