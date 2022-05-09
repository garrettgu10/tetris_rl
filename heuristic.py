from collections import deque

from tetris import Game
from gym import spaces
from typing import List
from time import sleep
from gym_env import game_to_observation, TetrisEnv

def simulate_game(weight_vector, heuristic, max_pieces=10e9, render=False):
    game = Game()
    score = pieces = 0
    gym_env = TetrisEnv()
    gym_env.game = game

    while not game.game_over and pieces < max_pieces:
        best_pos, best_score = (0, 0, 0), -10e9
        for position in game.find_possible_positions():
            newgame = game.clone()
            newgame.set_curr_position(position[0], position[1], position[2])
            newgame.hard_drop()
            cur_score = heuristic.predict(weight_vector, newgame)
            if cur_score > best_score:
                best_score = cur_score
                best_pos = position
        game.set_curr_position(best_pos[0], best_pos[1], best_pos[2])
        score += game.hard_drop()
        # game.add_cheese(1)
        if render: 
            game.print_game_state()
            gym_env.render()
        pieces += 1

    return score

# trained weights from https://codemyroad.wordpress.com/2013/04/14/tetris-ai-the-near-perfect-player/
# aggregate height: -0.510066
# complete lines: 0.760666
# holes: -0.35663
# bumpiness: -0.184483

class TetrisHeuristic():
    def __init__(self) -> None:
        self.scorers = [
            AggregateHeightScorer(),
            CompleteLinesScorer(),
            HolesScorer(),
            HoleDisFactorScorer(),
            HoleDisFactor2Scorer(),
            BumpinessScorer(),
            MaxHeightScorer(),
            TSpin3Scorer(),
            DiffFactorScorer()
        ]

    def num_heuristics(self):
        return len(self.scorers)

    def predict(self, weight: List[float], game: Game):
        assert len(weight) == self.num_heuristics()
        state = game_to_observation(game)
        return sum([weight[i] * scorer.score(state) for i, scorer in enumerate(self.scorers)])

class BeamSearchHeuristic():
    def __init__(self, wrapped_heuristic: TetrisHeuristic, beta: int, depth: int, eval_limit: int) -> None:
        self.wrapped_heuristic = wrapped_heuristic
        self.beta = beta
        self.depth = depth
        self.eval_limit = eval_limit
        self.gamma = 0.8
    
    def predict(self, weight: List[float], game: Game):
        open_list = deque([(game, 0, 0)])
        best_score_at_each_depth = [-10e9] * self.depth
        evaluated_positions = 0

        while open_list:
            game, score, depth = open_list.popleft()

            best_score_at_each_depth[depth] = max(best_score_at_each_depth[depth], score)

            if evaluated_positions >= self.eval_limit:
                break

            if depth == self.depth - 1:
                continue

            eval_limit_exceeded = False
            
            neighbors = []
            for position in game.find_possible_positions():
                newgame = game.clone()
                newgame.set_curr_position(position[0], position[1], position[2])
                drop_score = newgame.hard_drop()
                drop_score += self.wrapped_heuristic.predict(weight, newgame)
                neighbors.append((newgame, score + drop_score, depth + 1))

                evaluated_positions += 1
                if evaluated_positions >= self.eval_limit:
                    eval_limit_exceeded = True
                    break
            
            if eval_limit_exceeded:
                break

            open_list.extend(sorted(neighbors, key=lambda x: x[1], reverse=True)[:self.beta])

        for score in reversed(best_score_at_each_depth):
            if score > -10e9:
                return score

def columnHeight(board: spaces.Box, x: int) -> int:
    col_height = 0
    for y in range(40):
        if board[y][x] != 0:
            col_height = y + 1
    return col_height

class StateScorer(object):
    def __init__(self) -> None:
        pass

    def score(self, state: spaces.Dict) -> float:
        raise NotImplementedError

class AggregateHeightScorer(StateScorer):
    def __init__(self) -> None:
        pass
    
    def score(self, state: spaces.Dict) -> float:
        board:spaces.Box = state["board"]
        aggregate_height = 0
        for x in range(10):
            aggregate_height += columnHeight(board, x)
        return aggregate_height

class CompleteLinesScorer(StateScorer):
    def __init__(self) -> None:
        pass
    
    def score(self, state: spaces.Dict) -> float:
        return state["lines_completed"]

class WeightedHoleFactorScorer(StateScorer):
    def __init__(self) -> None:
        pass

    def hole_weight(self, y: int, max_height: int) -> float:
        raise NotImplementedError

    def score(self, state: spaces.Dict) -> float:
        board:spaces.Box = state["board"]
        holes = 0

        max_height = max([columnHeight(board, x) for x in range(10)])

        for x in range(10):
            holes_in_col = 0
            start_counting = False
            for y in range(39, -1, -1):
                if board[y][x] != 0:
                    start_counting = True
                elif start_counting:
                    holes_in_col += self.hole_weight(y, max_height)
            holes += holes_in_col
        return holes

class HolesScorer(WeightedHoleFactorScorer):
    def __init__(self) -> None:
        pass

    def hole_weight(self, y: int, max_height: int) -> float:
        return 1

class HoleDisFactor2Scorer(WeightedHoleFactorScorer):
    def hole_weight(self, y: int, max_height: int) -> float:
        if y < 10:
            return 1
        elif y < 20:
            return y / 10
        else:
            return 2

class HoleDisFactorScorer(WeightedHoleFactorScorer):
    def hole_weight(self, y: int, max_height: int) -> float:
        if y <= max_height - 5:
            return 0
        c = y - (max_height - 5)
        return y * c

class BumpinessScorer(StateScorer):
    def __init__(self) -> None:
        pass

    def score(self, state: spaces.Dict) -> float:
        board:spaces.Box = state["board"]
        heights = [columnHeight(board, x) for x in range(10)]

        bumpiness = 0
        for i in range(1, len(heights)):
            bumpiness += abs(heights[i] - heights[i - 1])
        
        return bumpiness

class MaxHeightScorer(StateScorer):
    def __init__(self) -> None:
        pass

    def score(self, state: spaces.Dict) -> float:
        board:spaces.Box = state["board"]

        return max([columnHeight(board, x) for x in range(10)])

class TSpin3Scorer(StateScorer):
    def __init__(self) -> None:
        pass

    def score(self, state: spaces.Dict) -> float:
        return 1 if state["lines_completed"] == 3 and state["last_move_was_tspin"] else 0

class HFactorScorer(StateScorer):
    def __init__(self) -> None:
        pass

    def score(self, state: spaces.Dict) -> float:
        board:spaces.Box = state["board"]
        heights = [columnHeight(board, x) for x in range(10)]
        
        tallest_height_idx = heights.index(max(heights))

        h_factor = 0
        
        if tallest_height_idx > 0:
            h_factor += heights[tallest_height_idx - 1]
        if tallest_height_idx < 9:
            h_factor += heights[tallest_height_idx + 1]
        
        return h_factor

class ClearUselessFactorScorer(StateScorer):
    def __init__(self) -> None:
        pass

    def score(self, state: spaces.Dict) -> float:
        board:spaces.Box = state["board"]

        heights = [columnHeight(board, x) for x in range(10)]
        avg_height = sum(heights) / 10.0

        return state["lines_completed"] * (avg_height - 10)

class DiffFactorScorer(StateScorer):
    def __init__(self) -> None:
        pass

    def score(self, state: spaces.Dict) -> float:
        board:spaces.Box = state["board"]
        heights = [columnHeight(board, x) for x in range(10)]
        avg_height = sum(heights) / 10.0

        return sum([abs(heights[i] - avg_height) for i in range(10)])