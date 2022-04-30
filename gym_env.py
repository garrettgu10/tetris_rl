import itertools
from gym import Env, spaces
from scorer import Scorer
from tetris import Game
from piece import PieceColor, Rotation
import numpy as np
import pygame

IDLE_REWARD = -0.01
INVALID_MOVE_REWARD = -10

def do_action(game: Game, action: int) -> float:
    if action == 7:
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
    return INVALID_MOVE_REWARD

class TetrisEnv(Env):
    def __init__(self):
        self.game = Game()
        self.observation_space = spaces.Dict(
            {
                "board": spaces.Box(0, 7, (40, 10), dtype=int),
                "piece": spaces.Box(1, 7, (1,), dtype=int),
                "piece_position": spaces.Box(0, 40, (2,), dtype=int),
                "can_swap": spaces.Box(0, 1, (1,), dtype=int),
                "upcoming_pieces": spaces.Box(1, 7, (4,), dtype=int),
            }
        )

        self.action_space = spaces.Discrete(8)
        self.window = None
        self.clock = None

        self.window_width = 640
        self.window_height = 480

    def reset(self, seed = None, return_info = False, options = None):
        self.game = Game(Scorer(), seed=seed)
        info = {}
        observation = game_to_observation(self.game)

        return (observation, info) if return_info else observation
    
    def step(self, action):
        reward = do_action(self.game, action)
        observation = game_to_observation(self.game)
        done = self.game.game_over
        info = {}

        return (observation, reward, done, info)
    
    def render(self, mode='human'):
        if self.window is None and mode == "human":
            pygame.init()
            pygame.display.init()
            self.window = pygame.display.set_mode((self.window_width, self.window_height))
        if self.clock is None and mode == "human":
            self.clock = pygame.time.Clock()
        
        canvas = pygame.Surface((self.window_width, self.window_height))

        canvas.fill((255, 255, 255))
        block_size = self.window_height // 20

        LEFT_OFFSET = 6 * block_size
        
        for y in range(19, -1, -1):
            for x in range(10):
                color = self.game.board.board[y][x]
                pygame.draw.rect(canvas, PieceColor.rgb_code(color), (LEFT_OFFSET + x * block_size, self.window_height - block_size - y * block_size, block_size, block_size))
        
        for point in self.game.curr_piece.shape.points:
            x = point[0] + self.game.curr_piece_x
            y = point[1] + self.game.curr_piece_y

            pygame.draw.rect(canvas, PieceColor.rgb_code(self.game.curr_piece.color), (LEFT_OFFSET + x * block_size, self.window_height - block_size - y * block_size, block_size, block_size))

        if self.game.swap_piece:
            for point in self.game.swap_piece.shape.points:
                x = point[0]
                y = point[1]

                pygame.draw.rect(canvas, PieceColor.rgb_code(self.game.swap_piece.color), (block_size + x * block_size, 4 * block_size - y * block_size, block_size, block_size))
        
        SWAP_PIECES_LEFT_OFFSET = LEFT_OFFSET + 11 * block_size
        
        for i in range(4):
            piece = self.game.bag[i]
            for point in piece.shape.points:
                x = point[0]
                y = point[1]

                pygame.draw.rect(canvas, PieceColor.rgb_code(piece.color), (SWAP_PIECES_LEFT_OFFSET + x * block_size, 4 * block_size * (i + 1) - y * block_size, block_size, block_size))

        
        if mode == "human":
            self.window.blit(canvas, canvas.get_rect())
            pygame.display.flip()
            pygame.event.pump()
            self.clock.tick(60)

        if mode == "rgb_array":
            return np.transpose(
                np.array(pygame.surfarray.pixels3d(canvas)), axes=(1, 0, 2)
            )
    
    def close(self):
        if self.window is not None:
            pygame.display.quit()
            pygame.quit()

#converts a game to an observation according to observation_shape
def game_to_observation(game: Game):
    board = game.board.board

    # convert board to array of ints
    board_array = np.zeros((40, 10), dtype=int)
    for y in range(40):
        for x in range(10):
            board_array[y][x] = board[y][x].value

    piece = game.curr_piece.color.value
    piece_position = [game.curr_piece_x, game.curr_piece_y]
    can_swap = 1 if game.can_swap else 0
    upcoming_pieces = list(itertools.islice(game.bag, 0, 4))
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