import pickle
import numpy as np
from gym import Env
from tetris import Game
from heuristic import TetrisHeuristic, simulate_game


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

    def predict(self, state):
        weight_vector = np.random.normal(self.mu, self.sd)
        return self.heuristic.predict(weight_vector, state)

    def train(self, games, episodes):
        '''
            'games' is the number of games a weight vector is evaluated on.
            'episodes' is the number of times we iterate on the weight distribution.
        '''

        for episode in range(episodes):
            if self.verbose: print(f'Starting episode {episode}')
            weights = [np.random.normal(self.mu, self.sd) for _ in range(self.N)]
            scores = [0] * self.N

            for weight_idx, weight_vector in enumerate(weights):
                for game in range(games):
                    if self.verbose: print(f'Starting game {game} for weight vector {weight_idx}')
                    scores[weight_idx] += simulate_game(weight_vector, self.heuristic)
    
            num_selected = int(self.rho * self.N)
            sorted_weights = sorted(zip(scores, weights), key=lambda x: -x[0])
            assert(sorted_weights[0][0] >= sorted_weights[-1][0])

            selected = [np.array(weight) for _, weight in sorted_weights][:num_selected]
            self.mu = np.mean(selected, axis=0)
            self.sd = np.mean(np.power(selected - self.mu, 2), axis=0) + self._noise(episode)
            assert len(self.mu) == self.heuristic.num_heuristics()
            assert len(self.sd) == self.heuristic.num_heuristics()
    
    def play_game(self):
        weights = np.random.normal(self.mu, self.sd) 
        score = simulate_game(weights, self.heuristic, render=True)
        print('Game terminated with score', score)

    def save(self, save_file):
        pickle.dump(self, open(save_file, "wb" ))