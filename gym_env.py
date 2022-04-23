from gym import Env, spaces
from scorer import Scorer
from tetris import Game
from piece import Rotation
import numpy as np

IDLE_REWARD = -0.01
INVALID_MOVE_REWARD = -10

def do_action(game: Game, action: int) -> float:
    if action == 0:
        return 0 if game.swap() else INVALID_MOVE_REWARD
    elif action == 1:
        return IDLE_REWARD if game.move(-1, 0) else INVALID_MOVE_REWARD
    elif action == 2:
        return IDLE_REWARD if game.move(0, -1) else INVALID_MOVE_REWARD
    elif action == 3:
        return IDLE_REWARD if game.move(1, 0) else INVALID_MOVE_REWARD
    elif action == 4:
        return IDLE_REWARD if game.rotate(Rotation.CCW) else INVALID_MOVE_REWARD
    elif action == 5:
        return IDLE_REWARD if game.rotate(Rotation.CW) else INVALID_MOVE_REWARD
    elif action == 6:
        return game.hard_drop()

class TetrisGym(Env):
    def __init__(self):
        self.game = Game()
        self.observation_shape = spaces.Dict(
            {
                "board": spaces.Box(0, 7, (40, 10), dtype=int),
                "piece": spaces.Box(1, 7, (1), dtype=int),
                "piece_position": spaces.Box(0, 40, (2), dtype=int),
                "can_swap": spaces.Box(0, 1, (1), dtype=int),
                "upcoming_pieces": spaces.Box(1, 7, (4), dtype=int),
            }
        )

        self.action_space(spaces.Discrete(7))

    def reset(self, seed = None, return_info = False, options = None):
        super().reset(seed=seed)
        self.game = Game(Scorer(), seed=seed)
        info = None
        observation = game_to_observation(self.game)

        return (observation, info) if return_info else observation
    
    def step(self, action):
        reward = do_action(self.game, action)
        observation = game_to_observation(self.game)
        done = self.game.game_over
        info = None

        return (observation, reward, done, info)

#converts a game to an observation according to observation_shape
def game_to_observation(game: Game):
    board = game.board.board

    # convert board to array of ints
    board_array = np.zeros((40, 10), dtype=int)
    for y in range(40):
        for x in range(10):
            board_array[y][x] = board[y][x]

    piece = game.curr_piece.color.value
    piece_position = [game.curr_piece_x, game.curr_piece_y]
    can_swap = 1 if game.can_swap else 0
    upcoming_pieces = game.bag[:4]
    # convert upcoming pieces to array of ints
    upcoming_pieces_array = np.zeros((4), dtype=int)
    for i in range(4):
        upcoming_pieces_array[i] = upcoming_pieces[i].color.value

    return {
        "board": board_array,
        "piece": piece,
        "piece_position": piece_position,
        "can_swap": can_swap,
        "upcoming_pieces": upcoming_pieces_array
    }

