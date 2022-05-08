import numpy as np
from ga import GeneticAlgoModel, Individual
from noisy_ce import NoisyCrossEntropyModel
from heuristic import TetrisHeuristic

def test_ga():
    ga_model = GeneticAlgoModel(pop_size=20, verbose=True, heuristic=TetrisHeuristic())
    ga_model.train(num_generations=3, num_games=5, max_pieces=10)
    # ga_model.play_game()

def test_nce():
    nce_model = NoisyCrossEntropyModel(N=10, rho=.1, noise_type='constant', verbose=True, heuristic=TetrisHeuristic())
    nce_model.train(games=1, episodes=2)
    # nce_model.play_game()

def test_individual():
    i = Individual(4)
    assert abs(np.linalg.norm(i.weights) - 1) < 0.0001

    prev_weights = np.array(i.weights, copy=True)
    i.mutate()
    new_weights = i.weights
    assert np.linalg.norm(prev_weights - new_weights) <= 0.2

if __name__ == '__main__':
    test_individual()
    test_ga()
    test_nce()