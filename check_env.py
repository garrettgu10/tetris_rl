from env_checker import check_env
from gym.wrappers import FlattenObservation
from gym_env import TetrisEnv

check_env(FlattenObservation(TetrisEnv()))