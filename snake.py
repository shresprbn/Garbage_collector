import pygame
import sys
from pygame.math import Vector2
import random

class Garbage:
    def __init__(self):
        self.randomize()
        
    def draw_garbage(self):
        #create rectangle
        garbage_rect = pygame.Rect(self.pos.x*cell_size,self.pos.y*cell_size,cell_size,cell_size)
        #draw
        pygame.draw.rect(screen,(126,166,114),garbage_rect)
    def randomize(self):
        self.x = random.randint(0,cell_number -1)
        self.y = random.randint(0,cell_number -1)
        self.pos = Vector2(self.x,self.y)

class Snake:
    def __init__(self):
        self.body = [Vector2(5,10),Vector2(4,10),Vector2(3,10)]
        self.direction = Vector2(1,0)
        self.new_block = False

    def draw_snake(self):
        for block in self.body:
            x_pos = block.x*cell_size
            y_pos = block.y*cell_size
            block_rect = pygame.Rect(x_pos,y_pos,cell_size,cell_size)
            pygame.draw.rect(screen,(183,111,122),block_rect)

    def move_snake(self):
        if self.new_block == True:
            body_copy = self.body[:]
            body_copy.insert(0,body_copy[0]+ self.direction)
            self.body = body_copy
            self.new_block = False
        else:
            body_copy = self.body[:-1]
            body_copy.insert(0,body_copy[0]+ self.direction)
            self.body = body_copy
            
    def add_block(self):
        self.new_block = True

class main:
    def __init__(self):
        self.snake = Snake()
        self.garbage = Garbage()
    
    def update(self):
        self.snake.move_snake()
        self.check_collision()
        self.check_fail()
    
    def draw_elements(self):
        self.garbage.draw_garbage()
        self.snake.draw_snake()
    
    def check_collision(self):
        if self.garbage.pos == self.snake.body[0]:
            self.garbage.randomize()
            self.snake.add_block()

    def check_fail(self):
        if not 0 <= self.snake.body[0].x < cell_number or not 0 <= self.snake.body[0].y < cell_number:
            self.game_over()
        for block in self.snake.body[1:]:
            if block == self.snake.body[0]:
                self.game_over()

    def game_over(self):
        pygame.quit()
        sys.exit()      

pygame.init()
cell_size =40 
cell_number = 20
screen = pygame.display.set_mode((cell_number*cell_size,cell_number*cell_size))
clock = pygame.time.Clock()
 
main_game = main()

SCREEN_UPDATE = pygame.USEREVENT
pygame.time.set_timer(SCREEN_UPDATE,150)

while True:
    #draw all the elements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == SCREEN_UPDATE:
            main_game.update()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and main_game.snake.direction.y != 1:
                main_game.snake.direction = Vector2(0,-1)    
            if event.key == pygame.K_DOWN and main_game.snake.direction.y != -1:
                main_game.snake.direction = Vector2(0,1)
            if event.key == pygame.K_RIGHT and main_game.snake.direction.x != -1:
                main_game.snake.direction = Vector2(1,0)
            if event.key == pygame.K_LEFT and main_game.snake.direction.x != 1:
                main_game.snake.direction = Vector2(-1,0)            
    screen.fill((175,215,70))
    main_game.draw_elements()
    pygame.display.update()
    clock.tick(60)
