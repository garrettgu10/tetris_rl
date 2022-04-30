from gym.utils.play import play

from gym_env import TetrisEnv

play(TetrisEnv(), keys_to_action = {
    (ord(' '),): 6,
    (ord('z'),): 7
})
