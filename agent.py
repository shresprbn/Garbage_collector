import torch
import random
import numpy as np
from collections import deque
from garbage import main, Direction, Point
from model import Linear_QNet, QTrainer
from helper import plot
from pygame.math import Vector2

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Agent:
    def __init__(self):
        self.n_games = 0
        self.eplison = 0 #control randomness
        self.gamma = 0.87 #discount rate
        self.memory = deque(maxlen=MAX_MEMORY) #popleft()
        self.model = Linear_QNet(11,256,3) 
        self.trainer = QTrainer(self.model, lr=LR,gamma=self.gamma)
        #TODO:model, trainer

    def check_vector_equal(self,vec,vec2):
        if vec.x == vec2[0] and vec.y == vec2[1]:
            return True
        return False

    def get_state(self,game):
        head = game.snake.body[0]
        # print(head)
        point_l = Vector2(head.x - 1, head.y)
        point_r = Vector2(head.x + 1, head.y)
        point_u = Vector2(head.x, head.y - 1)
        point_d = Vector2(head.x, head.y + 1)
        print(point_r)
        # print(game.snake.direction)
        #is not working

        dir_l = self.check_vector_equal(game.snake.direction,[-1,0])
        dir_r = self.check_vector_equal(game.snake.direction,[1,0])
        dir_u = self.check_vector_equal(game.snake.direction,[0,-1])
        dir_d = self.check_vector_equal(game.snake.direction,[0,1])
        state = [
            # Danger straight
            (dir_r and game.check_fail(point_r)) or 
            (dir_l and game.check_fail(point_l)) or 
            (dir_u and game.check_fail(point_u)) or 
            (dir_d and game.check_fail(point_d)),

            # Danger right
            (dir_u and game.check_fail(point_r)) or 
            (dir_d and game.check_fail(point_l)) or 
            (dir_l and game.check_fail(point_u)) or 
            (dir_r and game.check_fail(point_d)),

            # Danger left
            (dir_d and game.check_fail(point_r)) or 
            (dir_u and game.check_fail(point_l)) or 
            (dir_r and game.check_fail(point_u)) or 
            (dir_l and game.check_fail(point_d)),
            
            # Move direction
            dir_l,
            dir_r,
            dir_u,
            dir_d,
            
            # Food location 
            game.garbage.x < game.snake.body[0].x,  # food left
            game.garbage.x > game.snake.body[0].x,  # food right
            game.garbage.y < game.snake.body[0].y,  # food up
            game.garbage.y > game.snake.body[0].y  # food down
            ]
        # print(state)
        return np.array(state, dtype=int)

    def remember(self,state,action,reward,nextstate,done):
        self.memory.append((state,action,reward,nextstate,done)) #pop left if max mem

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory,BATCH_SIZE) #returns list of tuples
        else:
            mini_sample = self.memory

        states,actions,rewards,nextstates,dones = zip(*mini_sample)
        self.trainer.train_step(states,actions,rewards,nextstates,dones) 

    def train_short_memory(self,state,action,reward,nextstate,done):
        self.trainer.train_step(state,action,reward,nextstate,done) #store as tuple

    def get_action(self,state):
        #random shit in the beginning (exploration you know)
        self.eplison = 80 - self.n_games
        final_move = [0,0,0]
        if random.randint(0,200) < self.eplison:
            move = random.randint(0,2)
            print('random',move)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype = torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            print('chose from thing', move)
            final_move[move] = 1
        return final_move

def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = main()
    while True:
        #get old state
        state_old = agent.get_state(game)

        #get move
        final_move = agent.get_action(state_old)

        #perform move and get new state
        reward, done, score = game.play_step(final_move)
        done = not done
        # print(reward)
        # print(reward,done,score)
        
        state_new = agent.get_state(game)
        # print(game.snake.frame_iteration)
        # print(done)
        #train short memory
        agent.train_short_memory(state_old,final_move,reward,state_new,done)

        #remember shit
        agent.remember(state_old,final_move,reward,state_new,done)
        
        if done:
            #train long memory,plot result
            
            # print(game.snake.frame_iteration)
            game.game_over()
            agent.n_games+=1
            agent.train_long_memory()

            if score > record:
                record = score
                agent.model.save()
            print('GAME', agent.n_games,'Score',score,'Record', record)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score/ agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores,plot_mean_scores)
            

if __name__ == '__main__':
    train()