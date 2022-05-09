from noisy_ce import NoisyCrossEntropyModel
from heuristic import TetrisHeuristic

model = NoisyCrossEntropyModel(N=100, rho=.1, noise_type='zero', verbose=True, heuristic=TetrisHeuristic())
model.train(games=10, episodes=20, max_pieces=20, num_processes=24)
model.save('nce.pkl')
model.play_game()