import gym

from stable_baselines.common.policies import CnnPolicy
from stable_baselines import DQN

from gym.wrappers import FlattenObservation
from gym_env import TetrisEnv

env = FlattenObservation(TetrisEnv())

model = DQN(CnnPolicy, env, verbose=1)
model.learn(total_timesteps=100000)
model.save("dqn_tetris")

obs = env.reset()
while True:
    action, _states = model.predict(obs)
    obs, rewards, dones, info = env.step(action)
    env.render()