import pickle
from tracemalloc import start
import numpy as np
from gym import Env
from tetris import Game
from ga import Individual
from heuristic import TetrisHeuristic, simulate_game
from process_util import prep_sim, start_processes, end_processes, process_function, SimArgs
import time
from datetime import timedelta

'''
    This code was implemented by us, but it's based on a paper called
    "Learning Tetris using the Nosiy Cross-Entropy Method"
    by Szita and Lorincz. See our paper for a full citation.
'''

class NoisyCrossEntropyModel():
    def __init__(self, N: int, rho: float, noise_type: str, verbose: bool, heuristic: TetrisHeuristic) -> None:
        self.N = N
        self.rho = rho
        self.noise_type = noise_type
        self.verbose = verbose
        self.heuristic = heuristic
        self.mu = np.zeros(heuristic.num_heuristics())
        self.sd = np.ones(heuristic.num_heuristics()) * 100 

    def _noise(self, episode):
        if self.noise_type=='zero': return 0
        if self.noise_type=='constant': return 4
        if self.noise_type=='decreasing': return max(5 - episode/10, 0)
        raise NotImplementedError

    def predict(self, state: Game):
        weight_vector = np.random.normal(self.mu, self.sd)
        return self.heuristic.predict(weight_vector, state)

    def calc_selected(self, games, weights, max_pieces, num_processes):
        scores = [0] * self.N

        if num_processes == 1:
            for weight_idx, weight_vector in enumerate(weights):
                for game in range(games):
                    if self.verbose: print(f'Starting game {game} for weight vector {weight_idx}')
                    scores[weight_idx] += simulate_game(weight_vector, self.heuristic)
        else:
            population = [Individual(len(weights[0])) for _ in range(self.N)]
            for weight_idx, weight_vector in enumerate(weights):
                assert len(weight_vector) == len(population[weight_idx].weights)
                population[weight_idx].weights = weight_vector 
            assert all(map(lambda x: x.fitness < 0, population))

            args = SimArgs(num_games=games, max_pieces=max_pieces, heuristic=self.heuristic)
            chromosomes, modified = prep_sim(population, num_processes)
            processes = start_processes(num_processes, process_function, (chromosomes, modified, args))
            population = end_processes(processes, modified, num_processes)
            weights = [individual.weights for individual in population]
            scores  = [individual.fitness for individual in population]

        num_selected = int(self.rho * self.N)
        sorted_weights = sorted(zip(scores, weights), key=lambda x: -x[0])
        assert(sorted_weights[0][0] >= sorted_weights[-1][0])
        if self.verbose: print('Best score: ', max(scores))

        selected = [np.array(weight) for _, weight in sorted_weights][:num_selected]
        return selected

    def train(self, games, episodes, max_pieces, num_processes=1):
        '''
            'games' is the number of games a weight vector is evaluated on.
            'episodes' is the number of times we iterate on the weight distribution.
        '''

        for episode in range(episodes):
            start = time.time()
            weights = [np.random.normal(self.mu, self.sd) for _ in range(self.N)]
            selected = self.calc_selected(games, weights, max_pieces, num_processes)
            self.mu = np.mean(selected, axis=0)
            variance = np.mean(np.power(selected - self.mu, 2), axis=0) + self._noise(episode)
            self.sd = np.power(variance, .5)
            end = time.time()
            assert len(self.mu) == self.heuristic.num_heuristics()
            assert len(self.sd) == self.heuristic.num_heuristics()
            if self.verbose: 
                print(f'Episode {episode} terminated after {timedelta(seconds=end-start)} seconds')
    
    def play_game(self, num_pieces=100):
        weights = np.random.normal(self.mu, self.sd) 
        score = simulate_game(weights, self.heuristic, render=True, max_pieces=num_pieces)
        print('Game terminated with score', score)
        return score

    def save(self, save_file):
        pickle.dump(self, open(save_file, "wb" ))