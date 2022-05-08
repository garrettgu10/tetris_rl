from noisy_ce import NoisyCrossEntropyModel

model = NoisyCrossEntropyModel(N=100, rho=.1, noise_type='zero', verbose=True)
model.learn(games=30, episodes=100)
model.play_game()
model.save('nce.pkl')