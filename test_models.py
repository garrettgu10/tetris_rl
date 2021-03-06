from sys import argv
import numpy as np
from ga import GeneticAlgoModel, Individual
from noisy_ce import NoisyCrossEntropyModel
from heuristic import TetrisHeuristic, BeamSearchHeuristic
from heuristic import simulate_game
import pickle

def test_ga():
    ga_model = GeneticAlgoModel(pop_size=20, verbose=True, heuristic=TetrisHeuristic())
    ga_model.train(num_generations=3, num_games=5, max_pieces=10, num_processes=2)
    ga_model.play_game()

def test_nce():
    nce_model = NoisyCrossEntropyModel(N=100, rho=.1, noise_type='constant', verbose=True, heuristic=TetrisHeuristic())
    nce_model.train(games=1, episodes=2, max_pieces=500, num_processes=16)
    nce_model.play_game()

def test_individual():
    i = Individual(4)
    assert abs(np.linalg.norm(i.weights) - 1) < 0.0001

    prev_weights = np.array(i.weights, copy=True)
    i.mutate()
    new_weights = i.weights
    assert np.linalg.norm(prev_weights - new_weights) <= 0.2

if __name__ == '__main__':
    # test_individual()
    # test_ga()
    np.random.seed(0)
    # test_nce()
    # print("score: ", simulate_game([-0.510066, 0.760666, -0.35663, -0.184483, 0, 0, 0, 0, 0], TetrisHeuristic(), render=True))

    test_num = int(argv[1])

    ga = pickle.load(open('ga.pkl', 'rb'))
    nce = pickle.load(open('nce.pkl', 'rb'))
    nce2 = pickle.load(open('nce2.pkl', 'rb'))
    beam_heuristic = BeamSearchHeuristic(TetrisHeuristic(), 2, 2, 1000)
    regular_heuristic = TetrisHeuristic()

    model = [ga, nce, nce2][test_num % 3]
    heuristic = [beam_heuristic, regular_heuristic][test_num // 3]

    model.heuristic = heuristic
    score = model.play_game(num_pieces=200)
    print(score)
