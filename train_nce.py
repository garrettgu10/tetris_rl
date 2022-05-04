from gym_env import TetrisEnv
from noisy_ce import NoisyCrossEntropyModel

env = TetrisEnv()

model = NoisyCrossEntropyModel(env, N=100, rho=.1, noise_type='zero', verbose=True)
model.learn(games=30, episodes=100)
model.save("nce_tetris")

obs = env.reset()
while True:
    action = model.predict(obs)
    obs, rewards, dones, info = env.step(action)
    env.render()