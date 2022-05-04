import numpy as np
from gym import Env
from heuristic import TetrisHeuristic

class NoisyCrossEntropyModel():
    def __init__(self, env: Env, N: int, rho: float, noise_type: str, verbose: bool, heuristic: TetrisHeuristic) -> None:
        self.env = env
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

    def _simulate_game(self, weight_vector):
        state = self.env.reset()
        done, score = False, 0

        while not done:
            action = self.heuristic.predict(state, weight_vector)
            state, rewards, done, _ = self.env.step(action)
            score += rewards

        return score

    def predict(self, state):
        weight_vector = np.random.normal(self.mu, self.sd)
        return self.heuristic.predict(weight_vector, state)

    def train(self, games, episodes):
        '''
            'games' is the number of games a weight vector is evaluated on.
            'episodes' is the number of times we iterate on the weight distribution.
        '''

        for episode in episodes:
            if self.verbose: print(f'Starting episode {episode}')
            weights = [np.random.normal(self.mu, self.sd) for _ in range(self.N)]
            scores = np.zeros(self.N)

            for weight_idx, weight_vector in enumerate(weights):
                for game in games:
                    if self.verbose: print(f'Starting game {game} for weight vector {weight_idx}')
                    scores[weight_idx] += self._simulate_game(weight_vector)
    
            num_selected = int(self.rho * self.N)
            selected = [np.array(weight) for _, weight in sorted(zip(-scores, weights))][:num_selected]
            self.mu = np.mean(selected, axis=0)
            self.sd = np.power(selected - self.mu, 2) / num_selected + self._noise(episode)
