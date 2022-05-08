from noisy_ce import NoisyCrossEntropyModel

model = NoisyCrossEntropyModel(N=100, rho=.1, noise_type='zero', verbose=True)
model.train(games=30, episodes=100, max_pieces=500, num_processes=16)
model.play_game()
model.save('nce.pkl')